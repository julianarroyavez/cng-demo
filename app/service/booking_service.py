import datetime
import enum
import random
import uuid

from app import config
from app.database import db_session
from app.domain.booking_schema import Bookings, ServiceMasters, Slots, CancellationRefundDuration, BookingStatus
from app.domain.resource_schema import Stations, Vehicles, VehicleMasters, Nozzles, RatedPowers, ChargeTypes
from app.errors import UnknownError, ErrorMessages
from app.log import LOG
from app.repository.app_configs_repository import AppConfigRepository
from app.repository.bookings_repository import BookingsRepository
from app.repository.day_segments_repository import DaySegmentsRepository
from app.repository.nozzles_repository import NozzlesRepository
from app.repository.rated_powers_repository import RatedPowersRepository
from app.repository.service_masters_repository import ServiceMastersRepository
from app.repository.service_rates_repository import ServiceRatesRepository
from app.repository.slots_repository import SlotsRepository
from app.repository.users_repository import UsersRepository
from app.repository.vehicles_repository import VehiclesRepository
from app.service.notification_service import NotificationService
from app.service.slot_service import SlotService
from app.service.transaction_service import TransactionService
from app.util import string_util
from app.util.datetime_util import datetime_now, to_date, to_time, to_12_hour_format_with_meridian, \
    to_12_hour_format_without_meridian, to_day_of_week_in_binary, after_now, minutes_after_now, time_to_mins, \
    date_and_time_to_datetime, date_format
from app.util.datetime_util import get_rem_time_from_now, get_time_delta_in_minutes, before_given_time
from app.util.mqtt_publisher import send_booking_details, send_booking_details_for_temp
from app.util.notification_factory import NotificationFactory

booking_offset_url = "/api/v1/bookings?offset={key}"

name_format_string = "{} - {}"

hygge_box_number_string_format = '{hygge-box-number}'


class BookingService:
    class Links(enum.Enum):
        Self = "/api/v1/stations/{key}"  # todo: this should not be refer from here
        Next = booking_offset_url
        Last = booking_offset_url
        First = booking_offset_url

        def href(self, key):
            return self.value.format(**dict(key=key))

    def validate_booking_process(self, booking_req, user, vehicle, station):
        self.validate_booking_request(booking_req)
        self.validate_user_owns_vehicle(user, vehicle)
        self.validate_slot_availability(booking_req, station)
        self.validate_balance_availability(booking_req, user)

    def validate_booking_request(self, booking_req):
        pass  # empty function

    def validate_user_owns_vehicle(self, user, vehicle):
        pass  # empty function

    def validate_slot_availability(self, booking_req, station):
        pass  # empty function

    def validate_balance_availability(self, booking_req, user):
        pass  # empty function

    def generate_booking(self, booking_req, user, vehicle, station, nozzle_to_assign, charging_type):
        booking_repository = BookingsRepository()
        new_slot = SlotService().generate_slot_for_booking(booking_req=booking_req, nozzle=nozzle_to_assign, user=user)

        primary_key = uuid.uuid4()
        return booking_repository.insert(user=user, primary_key=primary_key, vehicle=booking_req['vehicle']['id'],
                                         station=station, new_slot=new_slot,
                                         service_date=to_date(booking_req['serviceDate']), status=BookingStatus.Booked,
                                         otp=string_util.generate_otp(),
                                         qr_code_data='/api/v1/booking/{}/scan'.format(primary_key),
                                         total_charges=booking_req['payment']['totalAmount']['value'],
                                         charging_type=charging_type)

    def process_booking(self, user_id, device_token, booking_req):
        service_masters_repository = ServiceMastersRepository()
        rated_powers_repository = RatedPowersRepository()
        vehicles_repository = VehiclesRepository()
        nozzles_repository = NozzlesRepository()
        users_repository = UsersRepository()
        slots_repository = SlotsRepository()
        bookings_repository = BookingsRepository()
        notification_factory = NotificationFactory()
        notification_service = NotificationService()

        LOG.info('inside transactions')

        now = datetime_now()

        user = users_repository.fetch_by_record_id(record_id=user_id, now=now)

        station = Stations.select().where((Stations.record_id == booking_req['station']['id'])).get()
        has_hygge_box = station.has_hygge_box

        columns = [Vehicles.record_id, Vehicles.registration_number, Vehicles.verified, VehicleMasters.record_id,
                   VehicleMasters.brand, VehicleMasters.model, VehicleMasters.manufacturing_year,
                   VehicleMasters.charging_connector_records]
        vehicle = vehicles_repository.fetch_by_id(columns=columns,
                                                  record_id=booking_req['vehicle']['id'],
                                                  now=now)

        columns = [ServiceMasters.id, ServiceMasters.record_id, ServiceMasters.name,
                   ServiceMasters.type, ServiceMasters.parameters]
        charging_service_master = service_masters_repository.fetch_by_record_id(
            columns=columns, now=now, record_id=booking_req['chargingService']['id'])

        columns = [RatedPowers.id, RatedPowers.record_id, RatedPowers.power, RatedPowers.power_unit,
                   RatedPowers.charge_type]

        applied_charging_rate = rated_powers_repository.fetch_by_record_id(
            columns=columns, now=now, record_id=booking_req['chargingService']['ratedPower']['id'])

        self.validate_booking_process(
            booking_req=booking_req,
            user=user,
            station=station,
            vehicle=vehicle
        )

        start_time_of_slot = to_time(booking_req['slot']['startTime'])
        end_time_of_slot = to_time(booking_req['slot']['endTime'])
        booked_nozzles = slots_repository.fetch_all_by_date(date=to_date(booking_req['serviceDate']),
                                                            start_time=start_time_of_slot,
                                                            end_time=end_time_of_slot)

        nozzles_available = nozzles_repository.fetch_all_available(now=now, record_id=station.record_id,
                                                                   applied_charging_rate=applied_charging_rate,
                                                                   vehicle=vehicle, booked_nozzles=booked_nozzles)

        if not nozzles_available:
            raise UnknownError(description='This slot is not available', message=ErrorMessages.SlotUnavailable.value)

        with db_session.atomic():
            booking = self.generate_booking(
                booking_req=booking_req,
                user=user,
                station=station,
                vehicle=vehicle,
                nozzle_to_assign=nozzles_available.first(),
                charging_type=applied_charging_rate.charge_type
            )

            day_segment = DaySegmentsRepository().fetch_by_id(booking_req['options']['segmentsOfDay'])

            days_of_week = to_day_of_week_in_binary(booking_req['serviceDate'])

            invoice = TransactionService().pay_for_booking(booking_req['context']['deviceToken'], user,
                                                           booking_req['payment']['totalAmount']['value'],
                                                           str(booking_req['chargingService']['rate']['id']),
                                                           days_of_week,
                                                           str(day_segment),
                                                           str(booking_req['chargingService']['id']),
                                                           str(booking_req['chargingService']['ratedPower']['id']))

            bookings_repository.update_deferred_transaction_id(booking_id=booking.booking_id, invoice_id=invoice.id)

            LOG.info('Booking %s' % booking_req)

            booking_data = {
                "booking": booking,
                "station": station
            }
            notification = notification_factory.create_and_queue_notification(data=booking_data, user_id=user_id,
                                                                              device=None,
                                                                              device_token=device_token,
                                                                              trigger='Booking_confirmation')

            notification_service.insert_notification(notifications=notification['notifications'],
                                                     to_device=notification['to_device'])

        connectors = []
        for connector in vehicle.vehicle_master.charging_connector_records:
            data = {
                "id": connector
            }
            connectors.append(data)

        response = {
            "bookingId": booking.booking_id,
            "serviceDate": booking.service_date.isoformat(),
            "serviceOtp": booking.otp,
            "status": booking.booking_status.value,
            "statusDesc": "",
            "qrCode": {
                "data": booking.qr_code_data
            },

            "slot": {
                "name": name_format_string.format(
                    to_12_hour_format_without_meridian(time=booking.slot.start_time),
                    to_12_hour_format_with_meridian(time=booking.slot.end_time)),
                "startTime": booking.slot.start_time.isoformat(),
                "endTime": booking.slot.end_time.isoformat(),
                "slotNumber": booking.slot.slot_number
            },
            "chargingService": {
                "id": charging_service_master.record_id,
                "name": charging_service_master.name,
                "type": charging_service_master.type.value,
                "subType": booking.charging_type.value,
                "ratedPower": {
                    "id": applied_charging_rate.record_id,
                    "power": applied_charging_rate.power,
                    "power_unit": applied_charging_rate.power_unit.value,
                    "chargingType": applied_charging_rate.charge_type.value
                }
            },
            "valueAddServices": [],
            "station": {
                "id": station.record_id,
                "name": station.name,
                "location": {
                    "latitude": float(station.location_latitude),
                    "longitude": float(station.location_longitude),
                    "address": station.address,
                    "pinCode": station.pinCode
                },
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(key=station.record_id)
                    }
                }
            },
            "vehicle": {
                'id': vehicle.record_id,
                'registrationNumber': vehicle.registration_number,
                'brand': vehicle.vehicle_master.brand,
                'model': vehicle.vehicle_master.model,
                'manufacturingYear': vehicle.vehicle_master.manufacturing_year,
                'makeYear': vehicle.vehicle_master.manufacturing_year,  # todo: correct this
                'vehicleMaster': {
                    'id': vehicle.vehicle_master.record_id
                },
                'verified': vehicle.verified
            },
            "payment": {
                "totalAmount": {
                    "value": booking_req['payment']['totalAmount']['value'],
                    "currency": "TOKEN"
                }
            }
        }
        response['vehicle']['connectors'] = connectors

        if has_hygge_box:
            self.__send_booking_to_topic(booking=response, hygge_box_number=station.hygge_box_number)
            app_configs_repository = AppConfigRepository()
            try:
                simulator = False
                app_config = app_configs_repository.fetch_hygge_box_simulation(now=datetime_now())
                if app_config.value == 'active':
                    simulator = True

                if simulator:

                    result = self.send_booking_popup_to_topic(
                        booking_id=response['bookingId'],
                        hygge_box_number=station.hygge_box_number,
                        start_time=response['slot']['startTime'],
                        end_time=response['slot']['endTime'],
                        is_scheduled=True
                    )
                    LOG.info('result: %s' % result)
            except Exception as e:
                LOG.error(f'error occurred due to {e}')

        return response

    def get_booking_details(self, booking_id):
        now = datetime_now()

        booking_repository = BookingsRepository()
        columns = [Bookings.service_date, Bookings.otp, Bookings.booking_status, Bookings.qr_code_data,
                   Bookings.slot_id, Bookings.charging_type, Slots.nozzle_record_id, Slots.start_time, Slots.end_time,
                   Slots.slot_number, Nozzles.rated_power_record_id, RatedPowers.record_id, RatedPowers.power,
                   RatedPowers.power_unit, RatedPowers.charge_type, Stations.station_code, Stations.name,
                   Stations.location_latitude, Stations.location_longitude, Stations.address, Stations.pinCode,
                   Vehicles.record_id, Vehicles.registration_number, Vehicles.vehicle_master_id, Vehicles.verified,
                   VehicleMasters.brand, VehicleMasters.model, VehicleMasters.manufacturing_year,
                   VehicleMasters.charging_connector_records, ServiceMasters.record_id,
                   ServiceMasters.name, ServiceMasters.type, ServiceMasters.parameters, Bookings.total_charges]
        booking_details = booking_repository.fetch_by_booking_id(
            columns=columns, now=now, booking_id=booking_id)

        booking_status = BookingStatus.Completed if (
                (datetime.datetime.combine(booking_details.service_date, booking_details.slots.end_time)
                 < datetime.datetime.now()) and (booking_details.booking_status.value != BookingStatus.Cancelled.value)
        ) else booking_details.booking_status

        connectors = []
        for connector in booking_details.vehicles.vehicle_masters.charging_connector_records:
            data = {
                "id": connector
            }
            connectors.append(data)

        response = {
            "bookingId": booking_id,
            "serviceDate": booking_details.service_date.isoformat(),
            "serviceOtp": booking_details.otp,
            "status": booking_status.value,
            "statusDesc": "",
            "qrCode": {
                "data": booking_details.qr_code_data
            },
            "slot": {
                "name": name_format_string.format(
                    to_12_hour_format_without_meridian(time=booking_details.slots.start_time),
                    to_12_hour_format_with_meridian(time=booking_details.slots.end_time)),
                "startTime": booking_details.slots.start_time.isoformat(),
                "endTime": booking_details.slots.end_time.isoformat(),
                "slotNumber": booking_details.slots.slot_number
            },
            "chargingService": {
                "id": booking_details.stations.station_services.service_masters.record_id,
                "name": booking_details.stations.station_services.service_masters.name,
                "type": booking_details.stations.station_services.service_masters.type.value,
                "subType": booking_details.charging_type.value,
                "ratedPower": {
                    "id": booking_details.slots.nozzles.rated_powers.record_id,
                    "power": booking_details.slots.nozzles.rated_powers.power,
                    "power_unit": booking_details.slots.nozzles.rated_powers.power_unit.value,
                    "chargingType": booking_details.slots.nozzles.rated_powers.charge_type.value
                }
            },
            "valueAddServices": [],
            "station": {
                "id": booking_details.stations.station_code,
                "name": booking_details.stations.name,
                "location": {
                    "latitude": booking_details.stations.location_latitude,
                    "longitude": booking_details.stations.location_longitude,
                    "address": booking_details.stations.address,
                    "pinCode": booking_details.stations.pinCode
                },
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(key=booking_details.stations.station_code)
                    }
                }
            },
            "vehicle": {
                "id": booking_details.vehicles.record_id,
                "registrationNumber": booking_details.vehicles.registration_number,
                "brand": booking_details.vehicles.vehicle_masters.brand,
                "model": booking_details.vehicles.vehicle_masters.model,
                "manufacturingYear": booking_details.vehicles.vehicle_masters.manufacturing_year,
                "makeYear": booking_details.vehicles.vehicle_masters.manufacturing_year,
                "vehicleMaster": {
                    "id": booking_details.vehicles.vehicle_master_id
                },
                "verified": booking_details.vehicles.verified
            },
            "payment": {
                "totalAmount": {
                    "value": booking_details.total_charges,
                    "currency": "TOKEN"
                }
            }
        }
        response['vehicle']['connectors'] = connectors
        return response

    def get_list_of_bookings(self, user_id, offset, limit):
        now = datetime_now()

        booking_repository = BookingsRepository()
        columns = [Bookings.booking_id, Bookings.service_date, Bookings.booking_status, Bookings.charging_type,
                   Slots.start_time, Slots.end_time, Slots.slot_number, Stations.station_code, Stations.name,
                   Stations.location_latitude, Stations.location_longitude, RatedPowers.charge_type]
        booking_details = booking_repository.fetch_all_by_user(columns=columns, user_id=user_id, now=now,
                                                               offset=offset, limit=limit)
        all_booking_details = []

        for booking in booking_details:
            booking_status = BookingStatus.Completed if (
                    (datetime.datetime.combine(booking.service_date, booking.slots.end_time)
                     < datetime.datetime.now()) and (booking.booking_status.value != BookingStatus.Cancelled.value)
            ) else booking.booking_status

            all_booking_details.append({
                "bookingId": booking.booking_id,
                "serviceDate": booking.service_date,
                "status": booking_status.value,
                "statusDesc": "",
                "slot": {
                    "name": name_format_string.format(
                        to_12_hour_format_without_meridian(time=booking.slots.start_time),
                        to_12_hour_format_with_meridian(time=booking.slots.end_time)),
                    "startTime": booking.slots.start_time.isoformat(),
                    "endTime": booking.slots.end_time.isoformat(),
                    "slotNumber": booking.slots.slot_number
                },
                "chargingService": {
                    "subType": booking.charging_type.value,
                    "ratedPower": {
                        "chargingType": booking.slots.nozzles.rated_powers.charge_type.value
                    }
                },
                "station": {
                    "id": booking.stations.station_code,
                    "name": booking.stations.name,
                    "location": {
                        "latitude": booking.stations.location_latitude,
                        "longitude": booking.stations.location_longitude
                    },
                    "_links": {
                        "self": {
                            "href": self.Links.Self.href(key=booking.stations.station_code)
                        }
                    }
                }
            })

        LOG.info('booking_details %s' % all_booking_details)
        return {
            "offset": offset,
            "limit": limit,
            "bookings": all_booking_details,
            "_links": {
                "next": {
                    "href": self.Links.Next.href(key=limit)
                },
                "last": {
                    "href": self.Links.Last.href(key='?')
                },
                "previous": None,
                "first": {
                    "href": self.Links.First.href(key=offset)
                }
            }
        }

    def cancel_booking(self, user_id, booking_id, device_token):

        with db_session.atomic():
            booking_repository = BookingsRepository()
            booking_repository.update_booking_status(booking_id, BookingStatus.Cancelled)
            transaction_service = TransactionService()
            notification_factory = NotificationFactory()
            notification_service = NotificationService()
            booking = booking_repository.fetch_charge_type_and_total_by_invoice_id(booking_id)
            penalty_amount = self.get_cancellation_penalty_amount(booking_id=booking_id,
                                                                  charge_type=booking.charging_type,
                                                                  amount=booking.invoices.orders.total)
            LOG.info(penalty_amount)
            transaction_service.cancel_booking(user_id=user_id, device_token=device_token,
                                               amount=booking.invoices.orders.total, penalty_amount=penalty_amount)

            columns = [Bookings.service_date, Bookings.otp, Bookings.booking_status, Bookings.qr_code_data,
                       Bookings.slot_id, Slots.nozzle_record_id, Slots.start_time, Slots.end_time, Slots.slot_number,
                       Nozzles.rated_power_record_id, RatedPowers.record_id, RatedPowers.power, RatedPowers.power_unit,
                       RatedPowers.charge_type, Stations.station_code, Stations.name, Stations.location_latitude,
                       Stations.location_longitude, Stations.address, Stations.pinCode, Vehicles.record_id,
                       Vehicles.registration_number, Vehicles.vehicle_master_id, Vehicles.verified,
                       VehicleMasters.brand,
                       VehicleMasters.model, VehicleMasters.manufacturing_year,
                       VehicleMasters.charging_connector_record,
                       ServiceMasters.record_id,
                       ServiceMasters.name, ServiceMasters.type, Bookings.total_charges,
                       Stations.has_hygge_box, Stations.hygge_box_number]
            booking_details = booking_repository.fetch_by_booking_id(columns=columns, now=datetime_now(),
                                                                     booking_id=booking_id)

            slots_repository = SlotsRepository()
            slot = slots_repository.fetch_by_id(booking_details.slot_id)
            slot.status = 'DISCARDED'
            slots_repository.update(slot)

            optiona_data = {
                "booking_station_name": booking_details.stations.name
            }

        notification = notification_factory.create_and_queue_notification(data=booking_id, user_id=user_id, device=None,
                                                                          device_token=device_token,
                                                                          trigger='Booking_cancellation',
                                                                          optional_data=optiona_data)

        notification_service.insert_notification(notifications=notification['notifications'],
                                                 to_device=notification['to_device'])
        notification_service.update_cancelled_notification(resource_id=notification['booking_id'],
                                                           events=notification['events'])

        has_hygge_box = booking_details.stations.has_hygge_box

        response = {
            "bookingId": booking_id,
            "serviceDate": booking_details.service_date.isoformat(),
            "serviceOtp": booking_details.otp,
            "status": booking_details.booking_status.value,
            "statusDesc": "",
            "qrCode": {
                "data": booking_details.qr_code_data
            },
            "slot": {
                "name": name_format_string.format(
                    to_12_hour_format_without_meridian(time=booking_details.slots.start_time),
                    to_12_hour_format_with_meridian(time=booking_details.slots.end_time)),
                "startTime": booking_details.slots.start_time.isoformat(),
                "endTime": booking_details.slots.end_time.isoformat(),
                "slotNumber": booking_details.slots.slot_number
            },
            "chargingService": {
                "id": booking_details.stations.station_services.service_masters.record_id,
                "name": booking_details.stations.station_services.service_masters.name,
                "type": booking_details.stations.station_services.service_masters.type.value,
                "ratedPower": {
                    "id": booking_details.slots.nozzles.rated_powers.record_id,
                    "power": booking_details.slots.nozzles.rated_powers.power,
                    "power_unit": booking_details.slots.nozzles.rated_powers.power_unit.value,
                    "chargingType": booking_details.slots.nozzles.rated_powers.charge_type.value
                }
            },
            "valueAddServices": [],
            "station": {
                "id": booking_details.stations.station_code,
                "name": booking_details.stations.name,
                "location": {
                    "latitude": booking_details.stations.location_latitude,
                    "longitude": booking_details.stations.location_longitude,
                    "address": booking_details.stations.address,
                    "pinCode": booking_details.stations.pinCode
                },
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(key=booking_details.stations.station_code)
                    }
                }
            },
            "vehicle": {
                "id": booking_details.vehicles.record_id,
                "registrationNumber": booking_details.vehicles.registration_number,
                "brand": booking_details.vehicles.vehicle_masters.brand,
                "model": booking_details.vehicles.vehicle_masters.model,
                "manufacturingYear": booking_details.vehicles.vehicle_masters.manufacturing_year,
                "makeYear": booking_details.vehicles.vehicle_masters.manufacturing_year,
                "vehicleMaster": {
                    "id": booking_details.vehicles.vehicle_master_id
                },
                "connector": {
                    "id": booking_details.vehicles.vehicle_masters.charging_connector_record
                },
                "verified": booking_details.vehicles.verified
            },
            "payment": {
                "totalAmount": {
                    "value": booking_details.total_charges,
                    "currency": "TOKEN"
                }
            }
        }
        if has_hygge_box:
            self.__send_booking_to_topic(booking=response, hygge_box_number=booking_details.stations.hygge_box_number)
        return response

    def get_cancellation_penalty_amount(self, booking_id, charge_type, amount):

        booking_repository = BookingsRepository()
        LOG.info('inside get_cancellation_penalty_amount')
        bookings = booking_repository.fetch_slot_start_time(booking_id)
        LOG.info('before slot start time')
        LOG.info(bookings.slot_start_time)
        rem_time_in_min = get_time_delta_in_minutes(get_rem_time_from_now(timestamp=bookings.slot_start_time))
        LOG.info(rem_time_in_min)
        if rem_time_in_min > CancellationRefundDuration.FullRefund.value:
            return 0
        service_rates_repository = ServiceRatesRepository()

        LOG.info('charge type % s' % charge_type)
        if rem_time_in_min > CancellationRefundDuration.Refund15min.value:
            if charge_type == ChargeTypes.SlowCharge:
                service_rate = service_rates_repository.fetch_by_service_rate_id(service_rate_id=3)  # todo fix this

            else:
                service_rate = service_rates_repository.fetch_by_service_rate_id(service_rate_id=6)  # todo fix this

            return service_rate.rate

        return amount

    def get_cancellation_confirmation(self, booking_id):

        booking_repository = BookingsRepository()
        LOG.info('inside get_cancellation_penalty_amount')

        bookings = booking_repository.fetch_slot_start_time(booking_id)

        LOG.info('before slot start time')
        LOG.info(bookings.slot_start_time)

        service_rates_repository = ServiceRatesRepository()
        booking = booking_repository.fetch_charge_type_and_total_by_invoice_id(booking_id)

        penalties = []

        LOG.info('charge type % s' % booking.charging_type)

        slot_start_time = bookings.slot_start_time

        if booking.charging_type == ChargeTypes.SlowCharge:
            service_rate = service_rates_repository.fetch_by_service_rate_id(service_rate_id=3)  # todo fix this
            partial_penalty = service_rate.rate

        else:
            service_rate = service_rates_repository.fetch_by_service_rate_id(service_rate_id=6)  # todo fix this
            partial_penalty = service_rate.rate

        full_refund_time = before_given_time(timestamp=slot_start_time,
                                             minutes=CancellationRefundDuration.FullRefund.value)
        penalties.append({"time": full_refund_time.isoformat(),
                          "interval": CancellationRefundDuration.FullRefund.value,
                          "penalty": {
                              "value": 0,
                              "currency": "TOKEN"
                          }
                          })

        partial_refund_time = before_given_time(timestamp=slot_start_time,
                                                minutes=CancellationRefundDuration.Refund15min.value)
        penalties.append({"time": partial_refund_time.isoformat(),
                          "interval": CancellationRefundDuration.Refund15min.value,
                          "penalty": {
                              "value": partial_penalty,
                              "currency": "TOKEN"
                          }
                          })

        penalties.append({"time": partial_refund_time.isoformat(),
                          "interval": 0,
                          "penalty": {
                              "value": booking.invoices.orders.total,
                              "currency": "TOKEN"
                          }
                          })

        response = {
            'penalties': penalties
        }

        return response

    def __send_booking_to_topic(self, booking, hygge_box_number):
        try:
            booking_topic_name = config.TOPIC['booking_to_hygge_box']

            booking_topic_name = booking_topic_name.replace(hygge_box_number_string_format, hygge_box_number)
            application_name = config.TOPIC['application_name']

            send_booking_details(topic_name=booking_topic_name, application_name=application_name,
                                 booking=booking)
        except Exception as e:
            LOG.error("Failed to push notification in queue")
            LOG.error(e)

    def send_booking_popup_to_topic(self, booking_id, hygge_box_number, start_time=None, end_time=None,
                                    is_scheduled=False):
        try:
            booking_topic_name = config.SIMULATOR['hygge_box_simulator']
            booking_topic_name = booking_topic_name.replace(hygge_box_number_string_format, hygge_box_number)
            application_name = config.TOPIC['application_name']

            bookings_repository = BookingsRepository()

            columns = [Bookings.booking_id, Bookings.service_date, Slots.end_time, Slots.start_time, Slots.date]

            booking_from_db = bookings_repository.fetch_data_by_booking_id(
                booking_id=booking_id,
                columns=columns,
                now=datetime_now()
            )

            booking = {
                "resourceType": "BOOKING",
                "resource": {
                    "bookingId": booking_id,
                    "status": "FULFILLED"
                },
                "publishedOn": datetime_now()
            }

            if is_scheduled:

                booking["scheduledTime"] = date_format(date_and_time_to_datetime(date_value=booking_from_db.service_date,
                                                                     time_value=booking_from_db.slots.end_time,
                                                                     date_format='%Y-%m-%d %H:%M:%S'))
                booking["isScheduled"] = True

            LOG.info('******************************************************************************************')
            LOG.info(booking)
            LOG.info(is_scheduled)
            LOG.info('******************************************************************************************')
            send_booking_details_for_temp(topic_name=booking_topic_name, application_name=application_name,
                                          booking=booking)
            return {
                "message": "data sent successfully"
            }
        except Exception as e:
            LOG.error("Failed to push notification in queue")
            LOG.error(e)

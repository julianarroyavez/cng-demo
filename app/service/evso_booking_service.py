from app.domain.booking_schema import Bookings, Slots
from app.domain.resource_schema import RatedPowers, Nozzles, Stations, Vehicles, VehicleMasters
from app.dto.booking.booking_dto import QrCode, TotalAmount, PaymentDto, SlotDto, StationDto, BookingDto, VehicleDto, \
    VehicleMasterDto, BookingResponseEVSO, RegistrationCertificate
from app.dto.report.report_model_base import model_to_dict
from app.log import LOG
from app.repository.bookings_repository import BookingsRepository
from app.repository.charging_connectors_repository import ChargingConnectorsRepository
from app.repository.nozzles_repository import NozzlesRepository
from app.repository.users_repository import UsersRepository
from app.repository.verifications_repository import VerificationsRepository
from app.util.datetime_util import datetime_now, get_day_month_from_date, get_abb_year_from_date, get_date_from_string, \
    date_from_datetime, get_date_from_string_with_timezone, to_12_hour_format_without_meridian, \
    to_12_hour_format_with_meridian, get_day_month_from_date_with_timezone

slot_time_format_string = "{} - {}"


class EVSOBookingService:

    def get_evso_station_bookings(self, start_date, end_date, station_record_id, device_token,
                                  offset, limit, include_params):
        booking_repository = BookingsRepository()

        bookings_list = []

        columns = [Bookings.booking_id, Bookings.service_date, Bookings.otp, Bookings.booking_status,
                   Bookings.qr_code_data, Bookings.slot_id, Bookings.charging_type, Bookings.total_charges,
                   Slots.start_time, Slots.end_time, Slots.slot_number, Slots.nozzle,
                   Nozzles.rated_power_record_id,
                   RatedPowers.record_id, RatedPowers.power, RatedPowers.power_unit, RatedPowers.charge_type,
                   Stations.station_code, Stations.name, Stations.location_latitude, Stations.location_longitude,
                   Stations.address, Stations.pinCode,
                   Vehicles.record_id, Vehicles.registration_number, Vehicles.vehicle_master_id, Vehicles.verified,
                   Vehicles.registration_certificate_image, Vehicles.user_record,
                   VehicleMasters.brand, VehicleMasters.model, VehicleMasters.manufacturing_year,
                   VehicleMasters.charging_connector_records, VehicleMasters.image]

        bookings = booking_repository.fetch_bookings_by_station_id_by_date(
            columns=columns,
            station_record_id=station_record_id,
            start_date=start_date,
            end_date=end_date,
            now=datetime_now(),
            offset=offset,
            limit=limit
        )

        charging_connector_repository = ChargingConnectorsRepository()
        nozzles_repository = NozzlesRepository()
        verification_repository = VerificationsRepository()
        users_repository = UsersRepository()
        try:
            verification = verification_repository.fetch_by_station_record_id(station_record_id=station_record_id)
            value_available_from = date_from_datetime(verification.verification_time)
        except Exception:
            LOG.info('Station is not verified')
            value_available_from = None

        for booking_data in bookings:
            qr_code = QrCode(data=booking_data.qr_code_data)
            qr_code = model_to_dict(qr_code)

            nozzle = nozzles_repository.fetch_by_id(
                record_id=booking_data.slots.nozzle
            )

            connector = charging_connector_repository.fetch_name_by_id(
                record_id=nozzle.charging_connector_record,
                now=datetime_now()
            )

            included_params = {
                'payment': self.__get_payment_data(booking_data=booking_data),

                'slot': self.__get_booking_slot_data(booking_data=booking_data),

                'station': self.__get_station_data(booking_data=booking_data),

                'vehicle': self.__get_vehicle_data(booking_data=booking_data),
                'slot_time': slot_time_format_string.format(
                    to_12_hour_format_without_meridian(time=booking_data.slots.start_time),
                    to_12_hour_format_with_meridian(time=booking_data.slots.end_time)
                )
            }
            license_number = users_repository.fetch_license_by_id(user_id=booking_data.vehicles.user_record,
                                                                  now=datetime_now())

            booking_details = BookingDto(
                booking_data=booking_data,
                connector_type=connector,
                license_number=license_number,
                qr_code=qr_code,
                included_params=included_params,
                context=str(device_token),
                include_params=include_params
            )
            booking_details = model_to_dict(booking_details)
            bookings_list.append(booking_details)

        result = {
            'booking': bookings_list,
            'dateRange': self.__get_date_range_from_start_and_end_time(
                start_date=get_date_from_string_with_timezone(start_date),
                end_date=get_date_from_string_with_timezone(end_date)),
            'valueAvailableFrom': value_available_from
        }

        LOG.info('%s' % include_params)
        return result

    def __get_booking_slot_data(self, booking_data):
        slot = SlotDto(
            name=self.__get_slot_name_from_start_and_end_time(
                start_time=booking_data.slots.start_time,
                end_time=booking_data.slots.end_time
            ),
            start_time=booking_data.slots.start_time,
            end_time=booking_data.slots.end_time,
            slot_number=booking_data.slots.slot_number
        )
        return model_to_dict(slot)

    def __get_station_data(self, booking_data):
        station = StationDto(
            name=booking_data.stations.name,
            latitude=float(booking_data.stations.location_latitude),
            longitude=float(booking_data.stations.location_longitude),
            code=booking_data.stations.station_code
        )
        return model_to_dict(station)

    def __get_vehicle_data(self, booking_data):
        vehicle_master = VehicleMasterDto(
            id=booking_data.vehicles.record_id,
            model=booking_data.vehicles.vehicle_masters.model,
            maker=booking_data.vehicles.vehicle_masters.brand,
            year=booking_data.vehicles.vehicle_masters.manufacturing_year,
            image=booking_data.vehicles.vehicle_masters.image
        )
        vehicle_master = model_to_dict(vehicle_master)

        registration_certificate = RegistrationCertificate(image=booking_data.vehicles.registration_certificate_image)
        registration_certificate = model_to_dict(registration_certificate)

        vehicle = VehicleDto(
            vehicle_id=booking_data.vehicles.record_id,
            reg_number=booking_data.vehicles.registration_number,
            vehicle_master=vehicle_master,
            registration_certificate=registration_certificate
        )
        return model_to_dict(vehicle)

    def __get_payment_data(self, booking_data):
        total_amount = TotalAmount(
            value=float(booking_data.total_charges),
            currency='TOKEN'
        )
        payment = PaymentDto(
            total_amount=model_to_dict(total_amount)
        )
        return model_to_dict(payment)

    def __get_slot_name_from_start_and_end_time(self, start_time, end_time):
        return '%s - %s' % (start_time, end_time)

    def __get_date_range_from_start_and_end_time(self, start_date, end_date):
        result = '%s, %s - %s, %s' % (
        get_day_month_from_date_with_timezone(date=start_date), get_abb_year_from_date(date=start_date),
        get_day_month_from_date_with_timezone(date=end_date), get_abb_year_from_date(date=end_date))
        LOG.info(result)
        return result

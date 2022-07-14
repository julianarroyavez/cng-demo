from app.domain.booking_schema import Bookings, Slots, StationServices, ServiceMasters, ServiceTypes
from app.domain.resource_schema import Stations, Vehicles, VehicleMasters, Nozzles, RatedPowers
from app.domain.payment_schema import Invoices, Orders


class BookingsRepository:
    def insert(self, user, primary_key, vehicle, station, new_slot, service_date, status, otp,
               qr_code_data, total_charges, charging_type):
        return (Bookings
                .create(created_by=user.record_id,
                        modified_by=user.record_id,
                        booking_id=primary_key,
                        consumer_user=user.record_id,
                        vehicle=vehicle,
                        station=station,
                        slot=new_slot,
                        service_date=service_date,
                        booking_status=status,
                        otp=otp,
                        qr_code_data=qr_code_data,
                        total_charges=total_charges,
                        charging_type=charging_type))

    def fetch_by_booking_id(self, columns, now, booking_id):
        return (Bookings
                .select(*columns)
                .join_from(Bookings, Slots, attr='slots',
                           on=(Bookings.slot_id == Slots.id))
                .join_from(Slots, Nozzles, attr='nozzles',
                           on=((Slots.nozzle_record_id == Nozzles.record_id)
                               & (Nozzles.validity_end > now)
                               & (Nozzles.validity_start <= now)))
                .join_from(Nozzles, RatedPowers, attr='rated_powers',
                           on=((Nozzles.rated_power_record_id == RatedPowers.record_id)
                               & (RatedPowers.validity_end > now)
                               & (RatedPowers.validity_start <= now)))
                .join_from(Bookings, Stations, attr='stations',
                           on=((Bookings.station_record_id == Stations.record_id)
                               & (Stations.validity_end > now)
                               & (Stations.validity_start <= now)))
                .join_from(Stations, StationServices, attr='station_services',
                           on=((Stations.record_id == StationServices.station_record_id)
                               & (StationServices.validity_end > now)
                               & (StationServices.validity_start <= now)))
                .join_from(StationServices, ServiceMasters, attr='service_masters',
                           on=(StationServices.service_master_record_id == ServiceMasters.record_id))
                .join_from(Bookings, Vehicles, attr='vehicles',
                           on=((Bookings.vehicle_record_id == Vehicles.record_id)
                               & (Vehicles.validity_end > now)
                               & (Vehicles.validity_start <= now)))
                .join_from(Vehicles, VehicleMasters, attr='vehicle_masters',
                           on=((Vehicles.vehicle_master_id == VehicleMasters.record_id)
                               & (VehicleMasters.validity_end > now)
                               & (VehicleMasters.validity_start <= now)))
                .where((Bookings.booking_id == booking_id)
                       & (ServiceMasters.type == ServiceTypes.EvCharge))  # todo modify
                .get())

    def fetch_all_by_user(self, columns, user_id, now, offset, limit):
        return (Bookings
                .select(*columns)
                .join_from(Bookings, Slots, attr='slots',
                           on=(Bookings.slot_id == Slots.id))
                .join_from(Slots, Nozzles, attr='nozzles',
                           on=((Slots.nozzle_record_id == Nozzles.record_id)
                               & (Nozzles.validity_end > now)
                               & (Nozzles.validity_start <= now)))
                .join_from(Nozzles, RatedPowers, attr='rated_powers',
                           on=((Nozzles.rated_power_record_id == RatedPowers.record_id)
                               & (RatedPowers.validity_end > now)
                               & (RatedPowers.validity_start <= now)))
                .join_from(Bookings, Stations, attr='stations',
                           on=((Bookings.station_record_id == Stations.record_id)
                               & (Stations.validity_end > now)
                               & (Stations.validity_start <= now)))
                .where(Bookings.consumer_user_record_id == user_id)
                .order_by(Bookings.service_date.desc(), Bookings.modified_on.desc())
                .offset(offset)
                .limit(limit))

    def update_booking_status(self, booking_id, status):
        (Bookings
         .update(booking_status=status)
         .where(Bookings.booking_id == booking_id)
         .execute())

    def update_deferred_transaction_id(self, booking_id, invoice_id):
        (Bookings
         .update(deferred_transaction=invoice_id)
         .where(Bookings.booking_id == booking_id)
         .execute())

    def fetch_charge_type_and_total_by_invoice_id(self, booking_id):
        return (Bookings.select(Bookings.charging_type, Orders.total)
                .join_from(Bookings, Invoices, attr='invoices', on=(Bookings.deferred_transaction == Invoices.id))
                .join_from(Invoices, Orders, attr='orders', on=(Invoices.order == Orders.order_id))
                .where(Bookings.booking_id == booking_id)
                .get())

    def fetch_slot_start_time(self, booking_id):
        return (Bookings.select((Slots.date + Slots.start_time).alias('slot_start_time'))
                .join_from(Bookings, Slots, attr='slots', on=(Bookings.slot == Slots.id))
                .where(Bookings.booking_id == booking_id)
                .get())

    def fetch_bookings_by_station_id_by_date(self, columns, station_record_id, start_date, end_date, now, offset,
                                             limit):
        return (Bookings
                .select(*columns)
                .distinct()
                .join_from(Bookings, Slots, attr='slots',
                           on=(Bookings.slot_id == Slots.id))
                .join_from(Slots, Nozzles, attr='nozzles',
                           on=((Slots.nozzle_record_id == Nozzles.record_id)
                               & (Nozzles.validity_end > now)
                               & (Nozzles.validity_start <= now)))
                .join_from(Nozzles, RatedPowers, attr='rated_powers',
                           on=((Nozzles.rated_power_record_id == RatedPowers.record_id)
                               & (RatedPowers.validity_end > now)
                               & (RatedPowers.validity_start <= now)))
                .join_from(Bookings, Stations, attr='stations',
                           on=((Bookings.station_record_id == Stations.record_id)
                               & (Stations.validity_end > now)
                               & (Stations.validity_start <= now)))
                .join_from(Stations, StationServices, attr='station_services',
                           on=((Stations.record_id == StationServices.station_record_id)
                               & (StationServices.validity_end > now)
                               & (StationServices.validity_start <= now)))
                .join_from(Bookings, Vehicles, attr='vehicles',
                           on=((Bookings.vehicle_record_id == Vehicles.record_id)
                               & (Vehicles.validity_end > now)
                               & (Vehicles.validity_start <= now)))
                .join_from(Vehicles, VehicleMasters, attr='vehicle_masters',
                           on=((Vehicles.vehicle_master_id == VehicleMasters.record_id)
                               & (VehicleMasters.validity_end > now)
                               & (VehicleMasters.validity_start <= now)))
                .where((Bookings.station == station_record_id)
                       & ((Bookings.service_date >= start_date)
                          & (Bookings.service_date <= end_date))
                       ).order_by(Bookings.service_date.desc(), Slots.start_time.desc()).order_by()
                .offset(offset)
                .limit(limit)
                )

    def fetch_data_by_booking_id(self, columns, now, booking_id):
        return (Bookings
                .select(*columns)
                .join_from(Bookings, Slots, attr='slots',
                           on=(Bookings.slot_id == Slots.id))
                .where((Bookings.booking_id == booking_id))  # todo modify
                .get())

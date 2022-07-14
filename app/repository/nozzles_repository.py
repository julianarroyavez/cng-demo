from peewee import fn

from app.domain.resource_schema import Nozzles, Chargers


class NozzlesRepository:
    def fetch_all_by_station_power_and_connector_type(self, now, station_id, vehicle, rated_power_id):
        return (Nozzles
                .select(Nozzles.record_id)
                .join_from(Nozzles, Chargers,
                           on=((Nozzles.charger_record == Chargers.record_id)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .where((Chargers.station_record == station_id)
                       & (Nozzles.charging_connector_record.in_(vehicle.vehicle_master.charging_connector_records))
                       & (Nozzles.rated_power_record == rated_power_id)
                       & (Nozzles.validity_start <= now)
                       & (Nozzles.validity_end > now)))

    def fetch_all_available(self, now, record_id, applied_charging_rate, vehicle, booked_nozzles):
        return (Nozzles
                .select()
                .join_from(Nozzles, Chargers,
                           on=((Nozzles.charger_record == Chargers.record_id)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .where((Chargers.station_record == record_id)
                       & (Nozzles.rated_power_record == applied_charging_rate.record_id)
                       & (Nozzles.charging_connector_record.in_(vehicle.vehicle_master.charging_connector_records))
                       & (Nozzles.record_id.not_in(booked_nozzles))))

    def insert(self, charger_record_id, nozzle_serial_id, charging_connector_record_id, rated_power_record_id,
               asset_id, req_auth_claims):
        return (Nozzles
                .create(record_id=fn.currval('nozzles_id_seq'),
                        charger_record_id=charger_record_id,
                        created_by=req_auth_claims.get('user'),
                        modified_by=req_auth_claims.get('user'),
                        charging_connector_record_id=charging_connector_record_id,
                        rated_power_record_id=rated_power_record_id,
                        serial_id=nozzle_serial_id,
                        asset_id=asset_id))

    def fetch_serial_id_by_station_id_and_charger_id(self, station_id, now, charger_id):
        return (Nozzles
                .select(Nozzles.serial_id)
                .join_from(Nozzles, Chargers, on=((Nozzles.charger_record == Chargers.id)
                                                  & (Chargers.validity_start <= now)
                                                  & (Chargers.validity_end > now)))
                .where((Chargers.station_record_id == station_id)
                       & (Nozzles.charger_record == charger_id)
                       & (Nozzles.validity_start <= now)
                       & (Nozzles.validity_end > now)))

    def fetch_all_serial_id_by_station_id(self, station_id, now):
        return (Nozzles
                .select(Nozzles.serial_id)
                .join_from(Nozzles, Chargers, on=((Nozzles.charger_record == Chargers.id)
                                                  & (Chargers.validity_start <= now)
                                                  & (Chargers.validity_end > now)))
                .where((Chargers.station_record_id == station_id)
                       & (Nozzles.validity_start <= now)
                       & (Nozzles.validity_end > now)))

    def fetch_all_by_station(self, now, station_id):
        return (Nozzles
                .select(Nozzles.record_id)
                .join_from(Nozzles, Chargers,
                           on=((Nozzles.charger_record == Chargers.record_id)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .where((Chargers.station_record == station_id)
                       & (Nozzles.validity_start <= now)
                       & (Nozzles.validity_end > now)))

    def fetch_by_id(self, record_id):
        return Nozzles.select().where(Nozzles.record_id == record_id).get()

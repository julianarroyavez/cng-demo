from peewee import fn

from app.domain.auth_schema import Equipments, EquipmentStatus
from app.domain.resource_schema import Chargers, StationAssignment


class EquipmentsRepository:
    def insert(self, equipment_type, serial_id, product_id, model_id, asset_id, req_auth_claims):
        return (Equipments
                .create(record_id=fn.currval('equipments_id_seq'),
                        created_by=req_auth_claims.get('user'),
                        modified_by=req_auth_claims.get('user'),
                        status=EquipmentStatus.Active,
                        type=equipment_type,
                        serial_id=serial_id,
                        product_id=product_id,
                        model_id=model_id,
                        asset_id=asset_id))

    def fetch_all_by_type_and_station_id(self, columns, equipment_type, user_id, now):
        return (Equipments
                .select(*columns)
                .join_from(Equipments, Chargers, attr='chargers',
                           on=((Equipments.record_id == Chargers.record_id)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .join_from(Chargers, StationAssignment, attr='station_assignment',
                           on=((Chargers.station_record == StationAssignment.station_record_id)
                               & (StationAssignment.validity_start <= now)
                               & (StationAssignment.validity_end > now)))
                .where((StationAssignment.validity_start <= now)
                       & (Equipments.type == equipment_type)
                       & (StationAssignment.validity_end > now)
                       & (StationAssignment.user_record_id == user_id)
                       & (Equipments.validity_start <= now)
                       & (Equipments.validity_end > now)))

    def fetch_all_by_type_and_not_active_and_station_id(self, station_id, now):
        return (Equipments
                .select(Equipments.id)
                .join_from(Equipments, Chargers, attr='chargers',
                           on=((Equipments.record_id == Chargers.record_id)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .join_from(Chargers, StationAssignment, attr='station_assignment',
                           on=((Chargers.station_record == StationAssignment.station_record_id)
                               & (StationAssignment.validity_start <= now)
                               & (StationAssignment.validity_end > now)))
                .where((StationAssignment.validity_start <= now)
                       & (StationAssignment.validity_end > now)
                       & (Equipments.status != EquipmentStatus.Active)
                       & (Chargers.station_record == station_id)
                       & (Equipments.validity_start <= now)
                       & (Equipments.validity_end > now)).count())

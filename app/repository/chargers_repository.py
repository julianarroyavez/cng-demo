from app.domain.auth_schema import EquipmentStatus
from app.domain.resource_schema import Chargers


class ChargersRepository:
    def insert(self, record_id, charger_name, charger_rank, station_id, equipment_type, serial_id, product_id, model_id, asset_id,
               req_auth_claims):
        return (Chargers
                .create(id=record_id,
                        record_id=record_id,
                        name=charger_name,
                        rank=charger_rank,
                        status=EquipmentStatus.Active,
                        station_record_id=station_id,
                        created_by=req_auth_claims.get('user'),
                        modified_by=req_auth_claims.get('user'),
                        type=equipment_type,
                        serial_id=serial_id,
                        product_id=product_id,
                        model_id=model_id,
                        asset_id=asset_id))

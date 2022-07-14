from peewee import fn

from app.domain.dashboard_schema import StationMapping


class StationMappingRepository:
    def insert(self, station_record_id, user, station_client_code=None):
        return StationMapping.create(
            record_id=fn.currval('station_mapping_id_seq'),
            station_record_id=station_record_id,
            station_client_code=station_client_code,
            created_by=user,
            modified_by=user)

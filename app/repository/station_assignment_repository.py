from peewee import fn

from app.domain.resource_schema import StationAssignment


class StationAssignmentRepository:
    def insert(self, station_record_id, req_auth_claims, verified):
        return (StationAssignment
                .create(record_id=fn.currval('station_assignment_id_seq'),
                        user_record_id=req_auth_claims.get('user'),
                        created_by=req_auth_claims.get('user'),
                        modified_by=req_auth_claims.get('user'),
                        station_record_id=station_record_id,
                        verified=verified))

    def fetch_all_by_user_record_id(self, now, user_id):
        return (StationAssignment
                .select()
                .where((StationAssignment.validity_start <= now)
                       & (StationAssignment.validity_end > now)
                       & (StationAssignment.user_record_id == user_id)))

    def fetch_by_user_record_id(self, now, user_id):
        return (StationAssignment
                .get((StationAssignment.validity_start <= now)
                     & (StationAssignment.validity_end > now)
                     & (StationAssignment.user_record_id == user_id)))

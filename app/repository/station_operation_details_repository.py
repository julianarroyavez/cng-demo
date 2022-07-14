from peewee import fn

from app.domain.resource_schema import StationOperationDetails


class StationOperationDetailsRepository:
    def insert(self, station_record_id, req_auth_claims, operating_days, operation_start_time, operation_end_time):
        return (StationOperationDetails
                .create(record_id=fn.currval('station_operation_details_id_seq'),
                        station_record_id=station_record_id,
                        created_by=req_auth_claims.get('user'),
                        modified_by=req_auth_claims.get('user'),
                        operating_days=operating_days,
                        operation_start_time=operation_start_time,
                        operation_end_time=operation_end_time)
                )

    def fetch_by_station_id(self, station_id, now, now_in_datetime):
        day_bits = pow(2, now_in_datetime.weekday())
        return (StationOperationDetails
                .get((StationOperationDetails.station_record_id == station_id)
                     & (StationOperationDetails.validity_start <= now)
                     & (StationOperationDetails.validity_end > now)
                     & (StationOperationDetails.operating_days & day_bits != 0))
                )

    def is_operational_day(self, operation_detail_record, now_in_datetime):
        day_bits = pow(2, now_in_datetime.weekday())
        return (operation_detail_record.operating_days & day_bits) != 0

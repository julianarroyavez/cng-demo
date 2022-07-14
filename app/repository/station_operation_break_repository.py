from peewee import fn

from app.domain.resource_schema import StationOperationBreakDetails


class StationOperationBreakRepository:

    def fetch_all_by_station_id(self, station_id, now, now_in_datetime):
        day_bits = pow(2, now_in_datetime.weekday())
        return StationOperationBreakDetails.select()\
            .where((StationOperationBreakDetails.station_record_id == station_id)
                       & (StationOperationBreakDetails.validity_start <= now)
                       & (StationOperationBreakDetails.validity_end > now)
                       & (StationOperationBreakDetails.break_days & day_bits != 0))\
            .order_by(StationOperationBreakDetails.break_start_time)


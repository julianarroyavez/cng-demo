from app.domain.resource_schema import StationOperatingTimeMaster


class OperatingTimeMasterRepository:
    def fetch_all(self, now, operation_type):
        return StationOperatingTimeMaster.select().where(
            (StationOperatingTimeMaster.validity_start <= now)
            & (StationOperatingTimeMaster.validity_end > now)
            & (StationOperatingTimeMaster.operation_type == operation_type)
        ).get()

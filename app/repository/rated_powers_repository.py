from app.domain.resource_schema import RatedPowers


class RatedPowersRepository:
    def fetch_by_record_id(self, columns, now, record_id):
        return RatedPowers.select(
            *columns
        ).where(
            (RatedPowers.validity_start <= now)
            & (RatedPowers.validity_end > now)
            & (RatedPowers.record_id == record_id)
        ).get()

    def fetch_all(self, now=None):
        return RatedPowers.select(
            RatedPowers.record_id,
            RatedPowers.power,
            RatedPowers.power_unit,
            RatedPowers.charge_type
        ).where(
            (RatedPowers.validity_start <= now)
            & (RatedPowers.validity_end > now)
        )

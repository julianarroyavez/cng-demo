from app.repository.rated_powers_repository import RatedPowersRepository
from app.util.datetime_util import datetime_now


class RatedPowerService:

    def embed_rated_powers(self, root_body, user_id, params):
        rated_powers = RatedPowersRepository().fetch_all(now=datetime_now())

        rate_power_master_list = []
        for each_rate_power in rated_powers:
            rate_power_master_list.append({
                "id": each_rate_power.record_id,
                "name": '{}V'.format(format(each_rate_power.power).rstrip('0').rstrip('.')),
                "power": each_rate_power.power,
                "powerUnit": each_rate_power.power_unit.value,
                "chargingType": each_rate_power.charge_type.value
            })

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['ratedPowers'] = rate_power_master_list

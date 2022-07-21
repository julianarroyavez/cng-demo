import enum

from app.domain.booking_schema import ServiceMasters, ServiceTypes
from app.repository.service_masters_repository import ServiceMastersRepository
from app.repository.service_rates_repository import ServiceRatesRepository
from app.util import image_util
from app.util.datetime_util import datetime_now


class ServiceMasterService:
    class Links(enum.Enum):
        IconImage = '/api/v1/services/{key}/icon-image'

        def href(self, key):
            return self.value.format(**dict(key=key))

    def embed_master_service(self, root_body, user_id, params):
        type_list = []
        service_master_repository = ServiceMastersRepository()
        now = datetime_now()

        if 'value-add' in params['services.type']:
            type_list.append(ServiceTypes.ValueAdd)

            service_masters = service_master_repository.fetch_by_type(now=now, type_list=type_list)
            service_masters_list = []

            for service_master in service_masters:
                service_masters_list.append({
                    "id": service_master.record_id,
                    "name": service_master.name,
                    "type": service_master.type.value,
                    "rank": service_master.service_rank,
                    "iconImage": {
                        "href": self.Links.IconImage.href(key=service_master.record_id)
                    }
                })

            if root_body.get('_embedded', None) is None:
                root_body['_embedded'] = {
                    'services': service_masters_list
                }
            else:
                root_body['_embedded']['services'] = service_masters_list
            return root_body

    def get_station_services(self, station_id, filters, addons):
        service_rates_repository = ServiceRatesRepository()
        types_list = []
        for filter_type_value in filters.get('type', []):
            if filter_type_value == 'value-add':
                types_list.append(ServiceTypes.ValueAdd)
            elif filter_type_value == 'ev-charge':
                types_list.append(ServiceTypes.EvCharge)
            elif filter_type_value == 'cng':
                types_list.append(ServiceTypes.Cng)

        # todo: handle issue when no type filter available
        query_filter_where_condition = (ServiceMasters.type.in_(types_list)) if types_list else True

        now = datetime_now()
        # todo: use addons to define joins on query
        service_rates_of_station_services = \
            service_rates_repository.fetch_all_with_rates_and_power_by_station(
                now=now,
                station_id=station_id,
                query_filter_where_condition=query_filter_where_condition)

        station_services_dict = {}

        for service_rate in service_rates_of_station_services:
            station_services_dict[service_rate.service_record.record_id] = station_services_dict.get(
                service_rate.service_record.record_id, {
                    "id": service_rate.service_record.record_id,
                    "name": service_rate.service_record.name,
                    "type": service_rate.service_record.type.value,
                    'subType': service_rate.consumption_rate_record.rated_power_record.charge_type.value,
                    "ratedPowerDict": {},
                    "rates": []
                })

            station_services_dict[service_rate.service_record.record_id]['ratedPowerDict'][
                service_rate.consumption_rate_record.rated_power_record.record_id] = {
                "id": service_rate.consumption_rate_record.rated_power_record.record_id,
                "power": service_rate.consumption_rate_record.rated_power_record.power,
                "power_unit": service_rate.consumption_rate_record.rated_power_record.power_unit.value,
                "chargingType": service_rate.consumption_rate_record.rated_power_record.charge_type.value
            }
            station_services_dict[service_rate.service_record.record_id]['ratedPowers'] = list(
                station_services_dict[service_rate.service_record.record_id]['ratedPowerDict'].values())

            rate = {
                "id": service_rate.consumption_rate_record.record_id,
                "consumptionFrom": service_rate.consumption_rate_record.consumption_from,
                "consumptionTo": service_rate.consumption_rate_record.consumption_to,
                "consumptionUnit": service_rate.consumption_rate_record.consumption_unit.value,
                "rate": service_rate.consumption_rate_record.rate,
                "rateUnit": service_rate.consumption_rate_record.rate_unit.value,
                'daysOfWeek': service_rate.consumption_rate_record.days_of_week,
                'isDefault': service_rate.primary,
                'segmentsOfDay': [],
                'coveredRatedPowers': []
            }
            for segment_of_day in service_rate.consumption_rate_record.segments_of_day:
                rate['segmentsOfDay'].append({
                    'id': segment_of_day
                })
            for covered_rated_power in service_rate.consumption_rate_record.covered_rated_powers:
                rate['coveredRatedPowers'].append({
                    'id': covered_rated_power
                })
            station_services_dict[service_rate.service_record.record_id]['rates'].append(rate)

        for service_rate in service_rates_of_station_services:
            station_services_dict[service_rate.service_record.record_id].pop('ratedPowerDict', None)

        return {
            'services': list(station_services_dict.values())
        }

    def get_icons_of_service(self, service_id, size):
        day_segments_repository = ServiceMastersRepository()
        image = day_segments_repository.fetch_icon_image_by_id(service_id=service_id)

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

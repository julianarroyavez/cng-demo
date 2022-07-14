from app.domain.booking_schema import ServiceRates, ServiceMasters, ServiceRateTable, StationServices
from app.domain.resource_schema import RatedPowers
from peewee import fn


class ServiceRatesRepository:
    def fetch_all_with_rates_and_power_by_station(self, now, station_id, query_filter_where_condition):
        return ServiceRates.select(
            ServiceMasters.record_id,
            ServiceMasters.name,
            ServiceMasters.type,
            ServiceMasters.parameters,
            ServiceRates.primary,
            ServiceRateTable.record_id,
            ServiceRateTable.description,
            ServiceRateTable.consumption_from,
            ServiceRateTable.consumption_to,
            ServiceRateTable.consumption_unit,
            ServiceRateTable.rate,
            ServiceRateTable.rate_unit,
            ServiceRateTable.days_of_week,
            ServiceRateTable.segments_of_day,
            ServiceRateTable.covered_rated_powers,
            RatedPowers.record_id,
            RatedPowers.power,
            RatedPowers.power_unit,
            RatedPowers.charge_type,

        ).join_from(ServiceRates, StationServices,
                    on=((StationServices.custom_service_rate_record == ServiceRates.record_id)
                        & (StationServices.validity_start <= now)
                        & (StationServices.validity_end > now))) \
            .join_from(ServiceRates, ServiceMasters, attr='service_record',
                       on=((ServiceMasters.record_id == ServiceRates.service_record)
                           & (ServiceMasters.validity_start <= now)
                           & (ServiceMasters.validity_end > now))) \
            .join_from(ServiceRates, ServiceRateTable, attr='consumption_rate_record',
                       on=((ServiceRateTable.service_rate == ServiceRates.record_id)
                           & (ServiceRateTable.validity_start <= now)
                           & (ServiceRateTable.validity_end > now))) \
            .join_from(ServiceRateTable, RatedPowers, attr='rated_power_record',
                       on=((RatedPowers.record_id == fn.any(ServiceRateTable.covered_rated_powers))
                           & (RatedPowers.validity_start <= now)
                           & (RatedPowers.validity_end > now))) \
            .where(
            (StationServices.station_record_id == station_id)
            & (ServiceRates.validity_start <= now)
            & (ServiceRates.validity_end > now)
            & query_filter_where_condition
        ).order_by(ServiceMasters.service_rank)

    def fetch_by_service_rate_id(self, service_rate_id):
        return (ServiceRateTable.select()
                .where(ServiceRateTable.id == service_rate_id).get())

    def fetch_by_service_master_record_id(self, service_master_record_id, now):
        return (ServiceRates
                .select()
                .where((ServiceRates.service_record == service_master_record_id)
                       & (ServiceRates.primary == True)
                       & (ServiceRates.validity_start <= now)
                       & (ServiceRates.validity_end > now))
                .get())

    def fetch_distinct_consumption_duration(self, now):
        return ServiceRateTable.select(
            ServiceRateTable.consumption_to.cast('INTEGER'),
            ServiceRateTable.consumption_unit
        ).distinct().where(
            (ServiceRateTable.validity_start <= now)
            & (ServiceRateTable.validity_end > now)).order_by(ServiceRateTable.consumption_to.cast('INTEGER'))

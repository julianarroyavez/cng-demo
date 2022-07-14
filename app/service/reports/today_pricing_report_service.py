from app import log
from app.constant import dashboard_constant
from app.database import db_session
from app.dto.report.report_model_base import model_to_dict
from app.dto.report.report_model_price_table import DaySegments, Rates, ChargingServices, ConsumableDuration, \
    ReportModelPriceTable, PriceData
from app.repository.day_segments_repository import DaySegmentsRepository
from app.repository.service_rates_repository import ServiceRatesRepository
from app.repository.stations_repository import StationsRepository
from app.util.datetime_util import datetime_now

LOG = log.get_logger()


class TodayPricingReportService:

    def get_report_price_table_data(self, date, station_id):

        LOG.info('Retrieving Pricing table data')
        day_segment_repository = DaySegmentsRepository()

        day_segments = day_segment_repository.fetch_all()

        segments_of_day = self.__get_segments_of_day(day_segments=day_segments)
        consumable_durations = self.__get_consumable_durations()

        charging_services = self.__get_charging_services(station_id=station_id, now=datetime_now(), date=date)

        price_table = PriceData(day_segments=segments_of_day, charging_services=charging_services,
                                consumable_durations=consumable_durations)

        price_table = model_to_dict(price_table)

        response = ReportModelPriceTable(report_key=dashboard_constant.STATION_SERVICE_PRICE_DATA,
                                         report_type=dashboard_constant.DATA_TABLE,
                                         title=dashboard_constant.PRICE_TABLE_TITLE,
                                         price_table=price_table,
                                         value_from=date, value_till=date)
        return model_to_dict(response)

    def __get_segments_of_day(self, day_segments):
        segments_of_day = []
        for day_of_segment in day_segments:
            day_segment = DaySegments(name=day_of_segment.name, segment_id=day_of_segment.id,
                                      segment_start_time=day_of_segment.segment_start_time,
                                      segment_end_time=day_of_segment.segment_end_time, rank=day_of_segment.id)
            segment_of_day_dict = model_to_dict(day_segment)
            segments_of_day.append(segment_of_day_dict)
        return segments_of_day

    def __get_consumable_durations(self):
        service_rate_repository = ServiceRatesRepository()
        durations = service_rate_repository.fetch_distinct_consumption_duration(now=datetime_now())

        consumable_durations = []
        for duration in durations:
            consumable_duration = self.__create_consumable_duration(value=duration.consumption_to,
                                                                    unit=duration.consumption_unit.value)
            if consumable_duration is not None:
                consumable_durations.append(consumable_duration)

        return consumable_durations

    def __query_to_fetch_data_for_price_table(self, station_id, datetime_value, query, service_type, sub_type):
        cursor = db_session.execute_sql(query % (station_id, sub_type, datetime_value, datetime_value,
                                                 station_id, service_type, datetime_value, datetime_value,
                                                 datetime_value, datetime_value))
        return cursor

    def __process_single_price_table_data(self, row, date):

        if int(row[4]) == 1:
            default = True
        else:
            default = False

        rates = Rates(rate=str(int(row[3])), raw_value=float(row[3]), raw_unit=dashboard_constant.TOKEN,
                      day_segment_id=int(row[4]), consumption_from=float(row[0]), consumption_to=float(row[1]),
                      consumption_unit=str(row[2]), is_default=default, date=date)
        rates_dict = model_to_dict(rates)

        return rates_dict

    def __get_value_from_sub_type(self, sub_type):

        if sub_type == dashboard_constant.FAST_EV_CHARGING:
            return dashboard_constant.FAST_DC
        elif sub_type == dashboard_constant.SLOW_EV_CHARGING:
            return dashboard_constant.SLOW_DC
        return sub_type

    def __create_consumable_duration(self, value, unit):

        if int(value) == 15:
            return model_to_dict(ConsumableDuration(name=dashboard_constant.DURATION_15_MIN, value=int(value),
                                                    unit=unit, rank=1))
        if int(value) == 30:
            return model_to_dict(ConsumableDuration(name=dashboard_constant.DURATION_30_MIN, value=int(value),
                                                    unit=unit, rank=2))
        if int(value) == 60:
            return model_to_dict(ConsumableDuration(name=dashboard_constant.DURATION_60_MIN, value=int(value),
                                                    unit=unit, rank=3))
        return None

    def __get_charging_services(self, station_id, now, date):
        station_repository = StationsRepository()

        charging_services = station_repository.fetch_all_service_master_by_station(now=now, station_id=station_id)
        charging_services_response = []
        for charging_service in charging_services:
            sub_type = charging_service.get('parameters').get('charging_type')
            cursor = self.__query_to_fetch_data_for_price_table(
                station_id=station_id, datetime_value=date,
                query=dashboard_constant.PRICE_TABLE_RATES_QUERY_FOR_EACH_SERVICE,
                service_type=charging_service.get(dashboard_constant.TYPE).value,
                sub_type=sub_type
            )
            rates = []
            for row in cursor.fetchall():
                rate = self.__process_single_price_table_data(row=row, date=date)
                rates.append(rate)

            services = ChargingServices(
                name=self.__get_value_from_sub_type(sub_type=charging_service.get('parameters').get('charging_type')),
                service_id=int(charging_service.get(dashboard_constant.ID)),
                service_type=charging_service.get(dashboard_constant.TYPE).value,
                sub_type=sub_type, rates=rates
            )

            services_dict = model_to_dict(services)
            charging_services_response.append(services_dict)

        return charging_services_response

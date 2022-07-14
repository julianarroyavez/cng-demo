from app import log
from app.constant import dashboard_constant
from app.dto.report.report_model_base import ReportModelResponse, model_to_dict, DashboardCardResponse
from app.errors import ForbiddenError
from app.repository.stations_repository import StationsRepository
from app.repository.users_repository import UsersRepository
from app.service.reports.energy_consumption_service import EnergyConsumptionService
from app.service.reports.station_overview_kpi_report_service import StationOverviewKpiReportService
from app.service.reports.today_pricing_report_service import TodayPricingReportService
from app.util.datetime_util import get_min_and_max_of_month_range, datetime_now

LOG = log.get_logger()


class ReportService:

    def get_dashboard_cards(self, date, report_key, user_record_id, station_id):
        reports = []

        LOG.info('get cards for dashboard basis of their ranks')
        users_repository = UsersRepository()
        station_repository = StationsRepository()

        user = users_repository.fetch_by_record_id(record_id=user_record_id, now=datetime_now())
        station = station_repository.fetch_by_record_id(now=datetime_now(), station_id=station_id)

        if (not user.verified) or (not station[0].verified):
            raise ForbiddenError(description="permission denied")

        report_keys = list(report_key.split(','))

        if dashboard_constant.STATION_SERVICE_PRICE_DATA in report_keys:
            href = dashboard_constant.STATION_SERVICE_PRICE_DATA_API_URL % date
            report = self.__get_individual_report_data(report_type=dashboard_constant.DATA_TABLE,
                                                       report_key=dashboard_constant.STATION_SERVICE_PRICE_DATA, rank=1,
                                                       href=href, title=dashboard_constant.PRICE_TABLE_TITLE)
            reports.append(report)

        if dashboard_constant.STATION_OVERVIEW_KPI in report_keys:
            href = dashboard_constant.STATION_OVERVIEW_KPI_API_URL % date
            report = self.__get_individual_report_data(title=dashboard_constant.OVERVIEW_TITLE,
                                                       report_type=dashboard_constant.KPI_LIST,
                                                       report_key=dashboard_constant.STATION_OVERVIEW_KPI, rank=2,
                                                       href=href)
            reports.append(report)

        if dashboard_constant.STATION_ENERGY_CONSUMPTION_GRAPH in report_keys:
            report = self.__get_station_statistics_group_response_format(date=date)
            reports.append(report)

        response = DashboardCardResponse(reports=reports)
        return model_to_dict(response)

    def __get_station_statistics_group_response_format(self, date=None):

        LOG.info('appending stats card')
        date_range = get_min_and_max_of_month_range(date=date)
        reports = []
        energy_consumption_report = self.__get_individual_report_data(
            title=dashboard_constant.ENERGY_CONSUMPTION_TITLE,
            report_type=dashboard_constant.STATS_GRAPH,
            report_key=dashboard_constant.STATION_ENERGY_CONSUMPTION_GRAPH,
            rank=1,
            href=dashboard_constant.STATION_ENERGY_CONSUMPTION_GRAPH_API_URL % (date_range.get('start'),
                                                                                date_range.get('end')),
            active=True
        )
        reports.append(energy_consumption_report)

        outages_graph_report = self.__get_individual_report_data(
            title=dashboard_constant.OUTAGES_TITLE,
            report_type=dashboard_constant.STATS_GRAPH,
            report_key=dashboard_constant.OUTAGES_KEY,
            rank=2,
            href=dashboard_constant.STATION_OUTAGES_API_URL % date,
            active=False
        )
        reports.append(outages_graph_report)

        charger_wise_consumption = self.__get_individual_report_data(
            title=dashboard_constant.CHARGING_WISE_CONSUMPTION_TITLE,
            report_type=dashboard_constant.STATS_GRAPH,
            report_key=dashboard_constant.CHARGER_WISE_CONSUMPTION_KEY,
            rank=3,
            href=dashboard_constant.STATION_CHARGER_WISE_GRAPH_API_URL % date,
            active=False
        )
        reports.append(charger_wise_consumption)

        revenue_report = self.__get_individual_report_data(
            title=dashboard_constant.REVENUE_TITLE,
            report_type=dashboard_constant.STATS_GRAPH,
            report_key=dashboard_constant.REVENUE_KEY,
            rank=4,
            href=dashboard_constant.STATION_REVENUE_GRAPH_API_URL % date,
            active=False
        )
        reports.append(revenue_report)

        href = dashboard_constant.STATION_STATISTICS_GROUP_API_URL % date

        return model_to_dict(ReportModelResponse(report_type=dashboard_constant.REPORT_GROUP,
                                                 reports=reports,
                                                 report_key=dashboard_constant.STATION_STATISTICS_GROUP, rank=3,
                                                 href=href))

    def __get_individual_report_data(self, href, report_type, report_key, rank, title, active=None):

        LOG.info('appending %s' % report_key)

        return model_to_dict(ReportModelResponse(report_type=report_type, report_key=report_key, rank=rank, href=href,
                                                 title=title, active=active))

    def get_report_price_table_data(self, date, station_id):

        today_pricing_report_service = TodayPricingReportService()
        return today_pricing_report_service.get_report_price_table_data(date=date,
                                                                        station_id=station_id)

    def get_station_overview_kpi_report_data(self, date, station_id):

        station_overview_kpi_report_service = StationOverviewKpiReportService()
        return station_overview_kpi_report_service.get_kpi_report_data(date=date,
                                                                       station_id=station_id)

    def get_station_energy_consumption_statistics(self, date_till, station_id, date_from):

        energy_consumption_service = EnergyConsumptionService()
        return energy_consumption_service.get_energy_consumption_stat(date_till=date_till,
                                                                      date_from=date_from,
                                                                      station_id=station_id)

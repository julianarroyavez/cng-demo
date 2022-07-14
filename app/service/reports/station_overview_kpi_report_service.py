from app import log
from app.constant import dashboard_constant
from app.database import db_session
from app.dto.report.report_model_base import model_to_dict
from app.dto.report.report_model_kpi import TotalHours, Trend, ImageModel, KPI, ReportModelKPI, BookingCountByDate, \
    EnergyConsumed
from app.util.datetime_util import get_previous_date, get_previous_date_in_string, get_min_and_max_of_two_week_range, \
    get_previous_and_current_date_range

LOG = log.get_logger()


class StationOverviewKpiReportService:

    def get_kpi_report_data(self, date, station_id):
        LOG.info('get Station Overview KPI report data')

        previous_date = get_previous_date(date)

        date_range = get_previous_and_current_date_range(date=date)

        total_energy_consumed = self.__get_total_energy_consumed(
            station_id=station_id,
            date=date_range.get('end'),
            previous_date=date_range.get('start')
        )
        kpis = [total_energy_consumed]

        no_of_bookings = self.__get_total_booking_count(
            station_id=station_id,
            date=date,
            previous_date=previous_date
        )
        kpis.append(no_of_bookings)

        total_charging_durations = self.__get_total_charging_duration_kpi(
            station_id=station_id,
            date=date_range.get('end'),
            previous_date=date_range.get('start')
        )
        kpis.append(total_charging_durations)

        outages = self.__get_outages(
            station_id=station_id,
            date=date_range.get('end'),
            previous_date=date_range.get('start')
        )
        kpis.append(outages)

        station_overview_report = ReportModelKPI(report_key=dashboard_constant.STATION_OVERVIEW_KPI,
                                                 report_type='KPI_LIST', title='OVERVIEW', kpis=kpis,
                                                 value_till=date_range.get('end'),
                                                 value_from=date_range.get('start'))
        return model_to_dict(station_overview_report)

    def __get_data_from_query_for_station_by_date(self, query, station_id, min_date, max_date,
                                                  total_energy_or_hours=False, outage=False):
        if total_energy_or_hours:
            cursor = db_session.execute_sql(query % (station_id, min_date, max_date, max_date, min_date))
        elif outage:
            cursor = db_session.execute_sql(query % (max_date, station_id, max_date, max_date,
                                                     min_date, station_id, min_date, min_date))
        else:
            cursor = db_session.execute_sql(query % (station_id, min_date, max_date, max_date, min_date))
        return cursor

    def __get_total_charging_duration_kpi(self, station_id, date, previous_date):

        cursor = self.__get_data_from_query_for_station_by_date(
            query=dashboard_constant.TOTAL_DURATION_QUERY_FOR_EACH_STATION_BY_DATE,
            station_id=station_id,
            min_date=previous_date,
            max_date=date,
            total_energy_or_hours=True
        )
        rows = cursor.fetchall()
        total_hours = []

        name = dashboard_constant.CHARGING_DURATION_TITLE
        kpi_key = dashboard_constant.CHARGING_DURATION_KEY
        rank = 3
        icon = self.__get_url_for_each_kpi(href=dashboard_constant.CHARGING_DURATION_URL)
        valid_from = previous_date
        active = True

        if len(rows) > 0:
            count = 0
            duration_value = ''
            for row in rows:
                duration = TotalHours(date=row[0], hours=row[1], minutes=row[2], seconds=row[3])
                total_hour = duration.seconds / 3600.00
                if count == 0:
                    duration_value = self.convert_seconds_to_hour_min(seconds=duration.seconds)
                total_hours.append(total_hour)
                count += 1

            value = duration_value
            trend = self.__get_trend(arr=total_hours,
                                     previous_date=get_previous_date_in_string(previous_date))
        else:
            value = '0hr'
            trend = self.__get_trend(arr=total_hours,
                                     previous_date=get_previous_date_in_string(previous_date))

        charging_durations = KPI(name=name, kpi_key=kpi_key, value=value, trend=trend, rank=rank, icon=icon,
                                 valid_from=get_previous_date_in_string(valid_from), active=active)
        return model_to_dict(charging_durations)

    def __get_trend(self, arr, previous_date):
        for x1, x2 in zip(arr[:-1], arr[1:]):
            try:
                percent_change = round((x1 - x2) * 100 / x2, 2)
            except ZeroDivisionError:
                percent_change = 0.00

            if percent_change < 0.00:
                percent_change_with_unit = '%s%%' % percent_change
                return model_to_dict(Trend(value=percent_change_with_unit,
                                           trend_flow=dashboard_constant.TREND_DOWNWARDS,
                                           trend_from=previous_date,
                                           raw_value=percent_change))
            elif percent_change > 0.00:
                percent_change_with_unit = '+%s%%' % percent_change
                return model_to_dict(Trend(value=percent_change_with_unit,
                                           trend_flow=dashboard_constant.TREND_UPWARDS,
                                           trend_from=previous_date,
                                           raw_value=percent_change))

        return model_to_dict(Trend(value='0.00%', trend_flow=dashboard_constant.TREND_NONE,
                                   trend_from=previous_date,
                                   raw_value=0.00))

    def __get_url_for_each_kpi(self, href):
        return model_to_dict(ImageModel(href=href))

    def __get_total_booking_count(self, station_id, previous_date, date):

        cursor = self.__get_data_from_query_for_station_by_date(
            query=dashboard_constant.BOOKING_COUNT_FOR_EACH_STATION_BY_DATE,
            station_id=station_id,
            min_date=previous_date,
            max_date=date
        )
        bookings = []
        booking_trend_array = []
        name = dashboard_constant.NO_OF_BOOKING_TITLE
        kpi_key = dashboard_constant.NO_OF_BOOKING_KEY
        rank = 2
        icon = self.__get_url_for_each_kpi(href=dashboard_constant.NO_OF_BOOKING_URL)
        valid_from = previous_date
        active = True

        rows = cursor.fetchall()
        if len(rows) > 0:
            for row in rows:
                booking_count = BookingCountByDate(date=row[0], booking_count=row[1])
                booking_trend_array.append(booking_count.booking_count)
                bookings.append(booking_count)

            value = self.get_value_in_str(value=int(bookings[0].booking_count))
            trend = self.__get_trend(arr=booking_trend_array, previous_date=previous_date)
        else:
            value = '0'
            trend = self.__get_trend(arr=booking_trend_array, previous_date=previous_date)

        no_of_bookings = KPI(name=name, kpi_key=kpi_key, value=value, trend=trend, rank=rank, icon=icon,
                             valid_from=get_previous_date_in_string(valid_from), active=active)

        return model_to_dict(no_of_bookings)

    def __get_total_energy_consumed(self, station_id, previous_date, date):

        cursor = self.__get_data_from_query_for_station_by_date(
            query=dashboard_constant.ENERGY_CONSUMED_FOR_EACH_STATION_BY_DATE,
            station_id=station_id,
            min_date=previous_date,
            max_date=date,
            total_energy_or_hours=True
        )
        rows = cursor.fetchall()

        name = dashboard_constant.ENERGY_CONSUMED_TITLE
        kpi_key = dashboard_constant.ENERGY_CONSUMED_KEY
        rank = 1
        icon = self.__get_url_for_each_kpi(href=dashboard_constant.ENERGY_CONSUMED_URL)
        valid_from = previous_date
        active = True

        total_energy = []
        energy_consumed_array = []
        if len(rows) > 0:
            for row in rows:
                energy = EnergyConsumed(date=row[0], total_energy=row[1])
                energy_consumed_array.append(energy.total_energy)
                total_energy.append(energy)

            value = self.get_value_in_str(value=total_energy[0].total_energy, unit='kwh')
            trend = self.__get_trend(arr=energy_consumed_array, previous_date=previous_date)
        else:
            value = '0 kwh'
            trend = self.__get_trend(arr=energy_consumed_array, previous_date=previous_date)

        total_energy_consumed = KPI(name=name, kpi_key=kpi_key, value=value, trend=trend, rank=rank, icon=icon,
                                    valid_from=get_previous_date_in_string(valid_from), active=active)

        return model_to_dict(total_energy_consumed)

    def __get_outages(self, station_id, previous_date, date):

        cursor = self.__get_data_from_query_for_station_by_date(
            query=dashboard_constant.OUTAGES_FOR_EACH_STATION_BY_DATE,
            station_id=station_id,
            min_date=previous_date,
            max_date=date,
            total_energy_or_hours=False,
            outage=True
        )
        rows = cursor.fetchall()

        outage_array = []
        for row in rows:
            outage_array.append(int(row[0]))

        name = dashboard_constant.OUTAGES_TITLE
        kpi_key = dashboard_constant.OUTAGES_KEY
        rank = 4
        icon = self.__get_url_for_each_kpi(href=dashboard_constant.OUTAGES_URL)
        valid_from = previous_date
        active = True
        value = self.get_value_in_str(value=rows[0][0])

        trend = self.__get_trend(arr=outage_array, previous_date=previous_date)

        total_energy_consumed = KPI(name=name, kpi_key=kpi_key, value=value, trend=trend, rank=rank, icon=icon,
                                    valid_from=get_previous_date_in_string(valid_from), active=active)

        return model_to_dict(total_energy_consumed)

    def get_value_in_str(self, value, unit=''):
        result = str(value).zfill(2) + ' %s' % unit if value > 0 else '%s %s' % (value, unit)
        return result.strip()

    def convert_seconds_to_hour_min(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds / 3600
        
        if hour < 1:
            minutes = seconds / 60
            return "%02dm" % minutes

        if seconds % 3600 != 0:
            seconds %= 3600
            minutes = seconds / 60
            return "%dhr%02dm" % (hour, minutes)
        return "%dhr" % hour

from app import log
from app.constant import dashboard_constant
from app.dto.report.report_model_base import model_to_dict
from app.dto.report.report_model_stat_graph import Segment, ReportModelStatGraph, Statistics, DataPoint, Data
from app.repository.energy_consumption_repository import EnergyConsumptionRepository
from app.util.datetime_util import get_date_from_string, \
    convert_date_to_duration_month, get_previous_date_in_string, convert_date_to_text_format, add_date_with_min_time, \
    add_date_with_max_time

LOG = log.logging


class EnergyConsumptionService:

    def get_energy_consumption_stat(self, date_till, date_from, station_id):

        stats = self.__get_statistics(date=date_till, station_id=station_id, previous_date=date_from)
        statistics = stats.get('stats')
        value_available_from = stats.get('value_available_from')
        LOG.info('Getting Stat Graph')

        report_model_stat_graph = ReportModelStatGraph(
            report_key=dashboard_constant.STATION_ENERGY_CONSUMPTION_GRAPH,
            report_type=dashboard_constant.STATS_GRAPH,
            title=dashboard_constant.ENERGY_CONSUMPTION_TITLE,
            statistics=statistics,
            value_till=date_till,
            value_from=get_previous_date_in_string(date_from),
            value_available_from=value_available_from
        )

        return model_to_dict(report_model_stat_graph)

    def __get_statistics(self, date, station_id, previous_date):
        segments = self.__get_all_segments()
        data_points = self.__get_all_data_points()
        data_result = self.__get_all_data(station_id=station_id, date_start=previous_date,
                                          date_end=date)
        data = data_result.get('data_set')
        value_available_from = data_result.get('value_available_from')
        statistics = Statistics(segments=segments, data_points=data_points, data=data)
        result = {
            'stats': model_to_dict(statistics),
            'value_available_from': value_available_from
        }
        return result

    def __get_all_segments(self):

        segments = []
        day_segment = Segment(name='D', key='DAY', rank=1,
                              segment_length=self.__get_segment_duration_from_key(segment_key=dashboard_constant.DAY_KEY))
        segments.append(model_to_dict(day_segment))

        month_segment = Segment(name='M', key='MONTH', rank=2,
                                segment_length=self.__get_segment_duration_from_key(segment_key=dashboard_constant.MONTH_KEY))
        segments.append(model_to_dict(month_segment))

        return segments

    def __get_all_data_points(self):
        data_points = []

        solar_data_point = DataPoint(name=dashboard_constant.SOLAR, key=dashboard_constant.SOLAR_KEY,
                                     graph_color_hex=dashboard_constant.SOLAR_COLOR_HEX, rank=1)
        data_points.append(model_to_dict(solar_data_point))

        grid_data_point = DataPoint(name=dashboard_constant.GRID, key=dashboard_constant.GRID_KEY,
                                    graph_color_hex=dashboard_constant.GRID_COLOR_HEX, rank=2)
        data_points.append(model_to_dict(grid_data_point))

        dg_data_point = DataPoint(name=dashboard_constant.DG, key=dashboard_constant.DG_KEY,
                                  graph_color_hex=dashboard_constant.DG_COLOR_HEX, rank=3)
        data_points.append(model_to_dict(dg_data_point))

        return data_points

    def __get_all_data(self, station_id, date_start, date_end):
        energy_consumption_repository = EnergyConsumptionRepository()

        energy_consumptions = energy_consumption_repository.fetch_all_by_station_id_by_date(station_id=station_id,
                                                                                            min_date=date_start,
                                                                                            max_date=date_end)
        value_available_from = energy_consumption_repository.fetch_date_of_first_available_data()
        try:
            data_set = self.__get_month_data(station_id=station_id, date_start=date_start, date_end=date_end)
        except Exception:
            data_set = []

        for energy_consumption in energy_consumptions:

            total_value = energy_consumption.sum_of_solar_power \
                          + energy_consumption.sum_of_grid_power \
                          + energy_consumption.sum_of_dg_power
            data_points = []
            solar_data = DataPoint(key=dashboard_constant.SOLAR_KEY,
                                   value=dashboard_constant.KILO_WATT_HOUR,
                                   raw_value=int(energy_consumption.sum_of_solar_power)
                                   if energy_consumption.sum_of_solar_power.is_integer()
                                   else energy_consumption.sum_of_solar_power,
                                   percentage_value=self.get_percent(
                                       value=energy_consumption.sum_of_solar_power,
                                       total_value=total_value))
            data_points.append(model_to_dict(solar_data))

            grid_data = DataPoint(key=dashboard_constant.GRID_KEY,
                                  value=dashboard_constant.KILO_WATT_HOUR,
                                  raw_value=int(energy_consumption.sum_of_grid_power)
                                  if energy_consumption.sum_of_grid_power.is_integer()
                                  else energy_consumption.sum_of_grid_power,
                                  percentage_value=self.get_percent(value=energy_consumption.sum_of_grid_power,
                                                                    total_value=total_value)
                                  )
            data_points.append(model_to_dict(grid_data))

            dg_data = DataPoint(key=dashboard_constant.DG_KEY,
                                value=dashboard_constant.KILO_WATT_HOUR,
                                raw_value=int(energy_consumption.sum_of_dg_power)
                                if energy_consumption.sum_of_dg_power.is_integer
                                else energy_consumption.sum_of_dg_power,
                                percentage_value=self.get_percent(value=energy_consumption.sum_of_dg_power,
                                                                  total_value=total_value)
                                )
            data_points.append(model_to_dict(dg_data))

            data = Data(name=convert_date_to_text_format(str(energy_consumption.reading_date)),
                        segment_key=dashboard_constant.DAY_KEY,
                        segment_start_time=add_date_with_min_time(date=energy_consumption.reading_date),
                        segment_end_time=add_date_with_max_time(date=energy_consumption.reading_date),
                        data_points=data_points)

            data_set.append(model_to_dict(data))

        result = {
            'data_set': data_set,
            'value_available_from': value_available_from
        }

        return result

    def get_percent(self, value, total_value):
        LOG.info('%s %s' % (value, total_value))
        try:
            return round((value / total_value * 100), 2)
        except Exception:
            return 0.00

    def __get_month_data(self, station_id, date_start, date_end):
        energy_consumption_repository = EnergyConsumptionRepository()

        data_set = []

        monthly_energy_consumption = energy_consumption_repository.fetch_all_by_station_id_by_month(
            station_id=station_id,
            min_date=date_start,
            max_date=date_end)

        data_points = []
        total_value = monthly_energy_consumption.sum_of_solar_power \
                      + monthly_energy_consumption.sum_of_grid_power \
                      + monthly_energy_consumption.sum_of_dg_power

        solar_data = DataPoint(key=dashboard_constant.SOLAR_KEY,
                               value=dashboard_constant.KILO_WATT_HOUR,
                               raw_value=int(monthly_energy_consumption.sum_of_solar_power)
                               if monthly_energy_consumption.sum_of_solar_power.is_integer()
                               else monthly_energy_consumption.sum_of_solar_power,
                               percentage_value=self.get_percent(value=monthly_energy_consumption.sum_of_solar_power,
                                                                 total_value=total_value))
        data_points.append(model_to_dict(solar_data))

        grid_data = DataPoint(key=dashboard_constant.GRID_KEY,
                              value=dashboard_constant.KILO_WATT_HOUR,
                              raw_value=int(monthly_energy_consumption.sum_of_grid_power)
                              if monthly_energy_consumption.sum_of_grid_power.is_integer()
                              else monthly_energy_consumption.sum_of_grid_power,
                              percentage_value=self.get_percent(value=monthly_energy_consumption.sum_of_grid_power,
                                                                total_value=total_value)
                              )
        data_points.append(model_to_dict(grid_data))

        dg_data = DataPoint(key=dashboard_constant.DG_KEY,
                            value=dashboard_constant.KILO_WATT_HOUR,
                            raw_value=int(monthly_energy_consumption.sum_of_dg_power)
                            if monthly_energy_consumption.sum_of_dg_power.is_integer()
                            else monthly_energy_consumption.sum_of_dg_power,
                            percentage_value=self.get_percent(value=monthly_energy_consumption.sum_of_dg_power,
                                                              total_value=total_value)
                            )
        data_points.append(model_to_dict(dg_data))

        month_data = Data(name=convert_date_to_duration_month(get_date_from_string(date_end)),
                          segment_key=dashboard_constant.MONTH_KEY,
                          segment_start_time=add_date_with_min_time(date=date_start),
                          segment_end_time=add_date_with_max_time(date=date_end), data_points=data_points)

        data_set.append(model_to_dict(month_data))

        return data_set

    def __get_segment_duration_from_key(self, segment_key):
        if segment_key == dashboard_constant.DAY_KEY:
            return 'P1D'
        if segment_key == dashboard_constant.MONTH_KEY:
            return 'P1M'

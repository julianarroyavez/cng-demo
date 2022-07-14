from app.dto.report.report_model_base import ReportModelBase


class Segment:

    def __init__(self, name: str, key: str, rank: int, segment_length: str) -> None:
        self.name = name
        self.key = key
        self.rank = rank
        self.segment_length = segment_length


class DataPoint:

    def __init__(self, name: str = None, key: str = None, rank: int = None, graph_color_hex: str = None,
                 data_point_key: str = None, value: str = None, raw_value: int = None,
                 percentage_value: int = None) -> None:
        if name is not None:
            self.name = name
        if key is not None:
            self.key = key
        if rank is not None:
            self.rank = rank
        if graph_color_hex is not None:
            self.graph_color_hex = graph_color_hex
        if data_point_key is not None:
            self.data_point_key = data_point_key
        if value is not None:
            self.value = value
        if raw_value is not None:
            self.raw_value = raw_value
        if percentage_value is not None:
            self.percentage_value = percentage_value


class Data:

    def __init__(self, name: str, data_points: list, segment_key: str, segment_start_time: str,
                 segment_end_time: str) -> None:
        self.name = name
        self.data_points = data_points
        self.segment_key = segment_key
        self.segment_start_time = segment_start_time
        self.segment_end_time = segment_end_time


class Statistics:

    def __init__(self, segments: list, data_points: list = None, data: list = None) -> None:
        self.segments = segments
        if data_points is not None:
            self.data_points = data_points
        if data is not None:
            self.data = data


class ReportModelStatGraph(ReportModelBase):

    def __init__(self, report_key: str, report_type: str, title: str, statistics: Statistics, value_till: str,
                 value_from: str, value_available_from: str) -> None:
        super().__init__(report_key=report_key, report_type=report_type, title=title, value_till=value_till,
                         value_from=value_from)
        self.statistics = statistics
        self.value_available_from = value_available_from


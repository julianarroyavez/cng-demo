from app.dto.report.report_model_base import ReportModelBase


class DaySegments:

    def __init__(self, name: str, segment_id: int, segment_start_time: str, segment_end_time: str, rank: int) -> None:
        self.name = name
        self.id = segment_id
        self.segment_start_time = segment_start_time
        self.segment_end_time = segment_end_time
        self.rank = rank


class ChargingServices:

    def __init__(self, name: str, service_id: int, service_type: str, sub_type: str, rates: list = None) -> None:
        self.name = name
        self.id = service_id
        self.type = service_type
        self.sub_type = sub_type
        self.rates = rates


class Rates:

    def __init__(self, rate: str, raw_value: int, raw_unit: str, day_segment_id: int, consumption_from: float,
                 consumption_to: float, consumption_unit: str, is_default: bool, date: str) -> None:
        self.rate = rate
        self.raw_value = raw_value
        self.raw_unit = raw_unit
        self.day_segment_id = day_segment_id
        self.consumption_from = consumption_from
        self.consumption_to = consumption_to
        self.consumption_unit = consumption_unit
        self.is_default = is_default
        self.date = date


class ConsumableDuration:

    def __init__(self, name: str, value: int, unit: str, rank: int) -> None:
        self.name = name
        self.value = value
        self.unit = unit
        self.rank = rank


class PriceData:

    def __init__(self, day_segments: list, charging_services: list, consumable_durations: list) -> None:
        self.day_segments = day_segments
        self.charging_services = charging_services
        self.consumable_durations = consumable_durations


class ReportModelPriceTable(ReportModelBase):

    def __init__(self, report_key: str, report_type: str, title: str, price_table: PriceData, value_till: str,
                 value_from: str) -> None:
        super().__init__(report_key=report_key, report_type=report_type, title=title, value_till=value_till,
                         value_from=value_from)
        self.price_data = price_table

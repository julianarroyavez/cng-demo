from app.dto.report.report_model_base import ReportModelBase


class ImageModel:

    def __init__(self, href: str):
        self.href = href


class Trend:

    def __init__(self, value: str, trend_flow: str, trend_from: str, raw_value: int) -> None:
        self.value = value
        self.trend_flow = trend_flow
        self.trend_from = trend_from
        self.raw_value = float(raw_value)


class KPI:

    def __init__(self, kpi_key: str, name: str, value: str, trend: Trend, rank: int,
                 icon: ImageModel, valid_from: str, active: bool, description: str = None) -> None:
        self.kpi_key = kpi_key
        self.name = name
        if description is not None:
            self.description = description
        self.value = value
        self.trend = trend
        self.rank = rank
        self.icon = icon
        self.valid_from = valid_from
        self.active = active


class ReportModelKPI(ReportModelBase):

    def __init__(self, report_key: str, report_type: str, title: str, kpis: list, value_till: str, value_from: str) \
            -> None:
        super().__init__(report_key=report_key, report_type=report_type, title=title, value_till=value_till,
                         value_from=value_from)
        self.kpis = kpis


class TotalHours:

    def __init__(self, date, hours, minutes, seconds):
        self.date = date
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds


class BookingCountByDate:

    def __init__(self, date, booking_count):
        self.date = date
        self.booking_count = booking_count


class EnergyConsumed:

    def __init__(self, date, total_energy):
        self.date = date
        self.total_energy = total_energy


class Outages:

    def __init__(self, date, outage):
        self.date = date
        self.outage = outage



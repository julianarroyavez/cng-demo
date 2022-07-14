from app.dto.report.report_model_base import ReportModelBase


object_data = dict.fromkeys(['key', 'name'])
object_single_data = dict.fromkeys(['xLabelKey', 'yLabelKey', 'sectionKey', 'value'])


class TableData:

    def __init__(self, sections: list, x_labels: list, y_labels: list, data: list) -> None:
        self.sections = sections
        self.x_labels = x_labels
        self.y_labels = y_labels
        self.data = data


class ReportModelTable(ReportModelBase):

    def __init__(self, report_key: str, report_type: str, title: str, table_data: TableData, value_till: str,
                 value_from: str) -> None:
        super().__init__(report_key=report_key, report_type=report_type, title=title, value_till=value_till,
                         value_from=value_from)
        self.table_data = table_data


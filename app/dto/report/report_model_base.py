from typing import Dict, Any


class ReportModelBase:

    def __init__(self, report_key: str, report_type: str, title: str, value_till: str, value_from: str) -> None:
        self.report_key = report_key
        self.report_type = report_type
        self.title = title
        self.value_till = value_till
        self.value_from = value_from


class ReportModelResponse:

    def __init__(self, report_type: str, report_key: str, rank: int, href: str = None, reports=None,
                 title: str = None, active: bool = None) -> None:

        self.title = title
        self.report_type = report_type
        self.report_key = report_key
        self.rank = rank
        if reports is not None:
            self.reports = reports

        if href is not None:
            _self = {
                "href": href
            }
            _links = {
                "self": _self
            }
            self._links = _links

        if active is not None:
            self.active = active


def model_from_dict(s: Dict[str, Any]) -> Any:
    return Any(**s)


def model_to_dict(x: Any) -> Dict[str, Any]:
    return t_dict(vars(x))


class DashboardCardResponse:

    def __init__(self, reports: list) -> None:
        self.reports = reports


def snake_to_camel_case(word):
    words = word.split('_')
    if '' in words:
        words.remove('')
    if len(words) == 1:
        return word

    result = words[0].lower()
    del words[0]
    join_word = ''.join(x.capitalize() or '_' for x in words)
    return result + join_word


def t_dict(d):
    if isinstance(d, list):
        return [t_dict(i) if isinstance(i, (dict, list)) else i for i in d]
    return {snake_to_camel_case(a): t_dict(b) if isinstance(b, dict) else b for a, b in d.items()}

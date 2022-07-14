from app.domain.support.support_schema import QueryState, SupportQueryStatus
from app.dto.report.report_model_base import model_to_dict
from app.log import LOG


class SupportQuery:

    def __init__(self, query_id, status) -> None:
        self.id = query_id
        self.status = status


class QueryContext:

    def __init__(self, device_token, device_os_version, app_version, request, session_token=None) -> None:
        self.device_token = device_token
        self.device_os_version = device_os_version
        self.app_version = app_version
        if request:
            self.session_token = session_token


class QueryDto:

    def __init__(self, customer_email, phone_number, query_text, context=None, status=None, query_id=None,
                 response_by=None, response_date=None, response_comment=None, customer_user=None, query_date_time=None,
                 respondent=None, update=None) -> None:
        if query_id is not None:
            self.id = query_id
        self.customer_email = customer_email
        if phone_number:
            self.customer_phone = phone_number
        if query_text:
            self.query_text = query_text
        self.context = context
        self.response_by = response_by
        self.response_date = response_date
        self.response_comment = response_comment
        if customer_user:
            self.customer = customer_user
        if status and update:
            self.status = SupportQueryStatus.from_str(status)
        elif status:
            self.status = status.value
        if query_date_time:
            self.query_date_time = query_date_time
        if respondent:
            self.respondent = respondent


class FaqDto:

    def __init__(self, faq_id, rank, content_type, content_text, content_format, additional_text,
                 answer=None, parent=None) -> None:
        self.id = faq_id
        self.rank = rank
        self.content_type = content_type
        self.content_text = content_text
        self.content_format = content_format
        self.additional_text = additional_text
        if answer is not None:
            self.answer = answer
        if parent is not None:
            self.parent_id = parent


class QueryAttemptDto:

    def __init__(self, phone_number: str, device_token: str, state: QueryState, desc: str) -> None:
        self.phone_number = phone_number
        self.device_token = device_token
        self.state = state
        self.state_desc = desc


class UserSupportQueryDto:

    def __init__(self, name, pin_code, license_number, email, phone_number, verified):
        self.name = name
        self.pin_code = pin_code
        self.license_number = license_number
        self.email = email
        self.phone_number = phone_number
        self.verified = verified


class ResponseQueryDto:

    def __init__(self, customer_email, phone_number, query_text, context, status=None, query_id=None,
                 response_date=None, response_comment=None, customer_user=None, query_date_time=None,
                 respondent=None) -> None:
        self.id = query_id
        self.customer_email = customer_email
        self.customer_phone = phone_number
        self.query_text = query_text
        self.context = context
        self.response_date = response_date
        self.response_comment = response_comment
        self.customer = model_to_dict(QueryUser(user_id=customer_user))
        self.status = status
        self.query_date_time = query_date_time
        if respondent:
            self.respondent = model_to_dict(QueryUser(user_id=respondent))


class QueryUser:

    def __init__(self, user_id):
        self.id = user_id
        self._links = model_to_dict(UserLinks(user_id=user_id))


class UserLinks:

    def __init__(self, user_id):
        self.self = model_to_dict(UserLinkSelf(user_id=user_id))


class UserLinkSelf:

    def __init__(self, user_id):
        self.href = f'/users/{user_id}'



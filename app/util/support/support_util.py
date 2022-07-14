import re

from app import config
from app.domain.support.support_schema import QueryState
from app.dto.support.support_dto import QueryDto, QueryAttemptDto, QueryContext, FaqDto
from app.log import LOG
from app.repository.users_repository import UsersRepository
from app.service.token_service import decode_token
from app.util.datetime_util import datetime_now

phone_number_regex = 'phone_number_regex'
context = 'context'
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


class SupportUtil:

    def convert_query_req_body_to_dto_for_insert(self, req_body):

        query_context = self.get_query_context(
            device_token=req_body.get(context).get('deviceToken'),
            device_os_version=req_body.get(context).get('deviceOsVersion'),
            app_version=req_body.get(context).get('appVersion'),
            session_token=req_body.get(context).get('sessionToken')
        )

        return QueryDto(
            customer_email=req_body.get('customerEmail'),
            phone_number=req_body.get('customerPhoneNumber'),
            query_text=req_body.get('queryText'),
            context=query_context
        )

    def get_query_context(self, device_token, device_os_version, app_version, session_token):
        return QueryContext(
            device_token=device_token,
            device_os_version=device_os_version,
            app_version=app_version,
            session_token=session_token,
            request=True
        )

    def convert_to_query_attempt_dto_for_success(self, query_dto):
        return QueryAttemptDto(
            phone_number=query_dto.customer_phone,
            device_token=query_dto.context.device_token,
            state=QueryState.Success,
            desc='Query raised successfully'
        )

    def convert_to_query_attempt_dto_for_restricted(self, query_dto):
        return QueryAttemptDto(
            phone_number=query_dto.customer_phone,
            device_token=query_dto.device_token,
            state=QueryState.Restricted,
            desc='Raise query restricted for this account'
        )

    def get_user_id(self, session_token, phone_number):
        user_repository = UsersRepository()

        if session_token is not None:
            user_id = decode_token(session_token)
            return user_id.get('user')
        elif phone_number is not None:
            try:
                user = user_repository.fetch_by_phone_number(phone_number=phone_number, now=datetime_now())
                return user.record_id
            except Exception:
                audit_user = user_repository.fetch_prospect_user(now=datetime_now())
            return audit_user.record_id

    def check_valid_email(self, email_id):
        if re.fullmatch(regex, email_id) or email_id is None or not email_id:
            return True
        return False

    def check_valid_phone_number(self, phone_number):
        if phone_number is None:
            return False
        pattern = re.compile(config.SUPPORT[phone_number_regex])
        return pattern.match(phone_number)

    def convert_faq_to_faq_dto(self, faq):
        if faq.parent_id is None:
            return FaqDto(faq_id=faq.id, rank=faq.rank, content_type=faq.content_type.value,
                          content_text=faq.content_text, content_format=faq.content_format.value,
                          additional_text=faq.additional_text)
        else:
            return FaqDto(faq_id=faq.id, rank=faq.rank, content_type=faq.content_type.value,
                          content_text=faq.content_text, content_format=faq.content_format.value,
                          additional_text=faq.additional_text, parent=faq.parent_id)

    def convert_tuple_to_faq_dto(self, faq):
        if faq[5] is None:
            return FaqDto(faq_id=faq[0], rank=faq[6], content_type=faq[1],
                          content_text=faq[2], content_format=faq[3],
                          additional_text=faq[4])
        else:
            return FaqDto(faq_id=faq[0], rank=faq[6], content_type=faq[1],
                          content_text=faq[2], content_format=faq[3],
                          additional_text=faq[4], parent=faq[5])

    def convert_query_req_body_to_dto_for_update(self, req_body):
        respondent = req_body.get('respondent')
        respondent_id = respondent['id']
        return QueryDto(
            customer_email=req_body.get('customerEmail'),
            phone_number=req_body.get('customerPhoneNumber'),
            query_text=req_body.get('queryText'),
            status=req_body.get('status'),
            query_date_time=req_body.get('queryDateTime'),
            response_comment=req_body.get('responseComment'),
            response_date=req_body.get('responseDateTime'),
            respondent=respondent_id,
            query_id=req_body.get('id'),
            update=True
        )

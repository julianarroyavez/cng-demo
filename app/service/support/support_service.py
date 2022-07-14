from app import config
from app.constant import support_constant
from app.database import db_session
from app.domain.support.support_schema import QueryState, SupportQueryStatus, SupportQueries
from app.dto.report.report_model_base import model_to_dict
from app.dto.support.support_dto import SupportQuery, QueryDto, QueryContext, UserSupportQueryDto, ResponseQueryDto
from app.errors import InvalidParameterError, InvalidFieldError, FieldErrors, ForbiddenError
from app.log import LOG
from app.repository.support.faq_repository import FaqRepository
from app.repository.support.support_query_repository import SupportQueryRepository
from app.repository.users_repository import UsersRepository
from app.util import string_util
from app.util.datetime_util import datetime_now
from app.util.support.support_util import SupportUtil

limit = 'limit'

query_attempt_error_text = 'You have already raised %s queries . Please wait for the resolution'
customer_phone_number = 'customerPhoneNumber'
query_text = 'queryText'
status = 'status'
customer_text = 'customer'
respondent_text = 'respondent'


class SupportService:

    def validate_req_body_for_insert(self, query_dto):
        support_util = SupportUtil()
        text = query_dto.query_text.replace("\n", "")
        strings = text.strip().split(" ")
        for i in strings:
            LOG.info(i)
            if not string_util.check_if_alphanumeric(i):
                raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Query)])

        if not support_util.check_valid_email(email_id=query_dto.customer_email):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Email)])

        if not support_util.check_valid_phone_number(phone_number=query_dto.customer_phone):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

    def validate_req_body_for_update(self, query_dto):
        support_util = SupportUtil()
        text = query_dto.query_text.replace("\n", "")
        strings = text.strip().split(" ")
        for i in strings:
            LOG.info(i)
            if not string_util.check_if_alphanumeric(i):
                raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Query)])

        if not string_util.check_if_alphanumeric(query_dto.query_response):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Query)])

        if not string_util.check_if_alphanumeric(query_dto.query_status):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Query)])

        if not support_util.check_valid_email(email_id=query_dto.customer_email):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Email)])

        if not support_util.check_valid_phone_number(phone_number=query_dto.customer_phone):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

    def insert_raised_query(self, query_dto):
        with db_session.atomic():
            query_repository = SupportQueryRepository()
            support_util = SupportUtil()

            self.validate_req_body_for_insert(query_dto=query_dto)

            user_id = support_util.get_user_id(session_token=query_dto.context.session_token,
                                               phone_number=query_dto.customer_phone)

            self.__check_query_attempts(query_dto=query_dto)

            query = query_repository.insert(query_dto=query_dto, now=datetime_now(), user_id=user_id)

            return model_to_dict(
                SupportQuery(
                    query_id=query.id,
                    status=QueryState.Success.value
                )
            )

    def __check_query_attempts(self, query_dto):
        query_attempts = support_constant.GET_COUNT_OF_RAISED_QUERY_WITHIN_24_HOURS % (query_dto.customer_phone,
                                                                                       datetime_now(), datetime_now())
        cursor = db_session.execute_sql(query_attempts)
        query_attempts = cursor.fetchone()
        if query_attempts[0] >= int(config.SUPPORT[limit]):
            raise ForbiddenError(
                raw_exception=QueryState.Restricted.value,
                description=query_attempt_error_text % config.SUPPORT[limit],
                message=query_attempt_error_text % config.SUPPORT[limit]
            )

    def get_all_active_support_queries(self, expand, include, query_field, structure,
                                       date_range, result_set_limit, offset, query, sort, status):
        support_query_repository = SupportQueryRepository()

        active_statuses = SupportQueryStatus.get_active_query_status(status=status)

        columns = [SupportQueries.id, SupportQueries.created_on, SupportQueries.customer_email,
                   SupportQueries.response_comment, SupportQueries.response_date, SupportQueries.customer_device_token,
                   SupportQueries.customer_device_os_version, SupportQueries.customer_app_version,
                   SupportQueries.customer_user, SupportQueries.response_by]

        where_clauses_query_field = self.__create_clauses_on_query_fields(query_field=query_field, query=query)

        where_clauses_date_range = self.__create_clauses_on_date_range(date_range=date_range)

        sort_list = self.__create_sorting_order_and_direction(sort=sort)

        columns = self.__get_included_columns(include=include, columns=columns)

        queries_from_database = support_query_repository.fetch_all_active(
            all_active_status=active_statuses,
            columns=columns,
            limit=result_set_limit,
            offset=offset,
            where_clauses_query_field=where_clauses_query_field,
            where_clauses_date_range=where_clauses_date_range,
            sort=sort_list
        )

        queries = {}
        response = []
        for query in queries_from_database:
            context = QueryContext(
                device_token=query.customer_device_token,
                device_os_version=query.customer_device_os_version,
                app_version=query.customer_app_version,
                request=False
            )
            query_dto = QueryDto(
                customer_email=query.customer_email,
                phone_number=query.customer_phone,
                query_text=query.query_text,
                context=model_to_dict(context),
                query_id=query.id,
                response_by=query.response_by,
                response_date=query.response_date,
                response_comment=query.response_comment,
                customer_user=query.customer_user,
                status=query.status
            )
            query_data = model_to_dict(query_dto)
            query_data = self.__get_expanded_columns(expand=expand, customer=query.customer_user,
                                                     respondent=query.response_by, query_data=query_data)
            response.append(query_data)

        queries['supportQueries'] = response
        queries['offset'] = offset
        queries['limit'] = result_set_limit

        queries['_links'] = self.__create_links(offset=offset, result_set_limit=result_set_limit)

        return queries

    def get_all_faqs(self):
        faq_repository = FaqRepository()
        support_util = SupportUtil()
        result = []
        response = {}
        faqs = faq_repository.fetch_all_by_content_type_category_and_question()
        for faq in faqs:
            faq_dict = model_to_dict(support_util.convert_faq_to_faq_dto(faq=faq))
            try:
                leaf_node = faq_repository.fetch_answer_action_by_parent_id(parent_id=faq.id)
                faq_dict['answer'] = model_to_dict(support_util.convert_faq_to_faq_dto(faq=leaf_node))
            except Exception:
                LOG.error('No leaf node found for id %s' % faq.id)
            result.append(faq_dict)

        response['faqs'] = result

        return response

    def __get_included_columns(self, include, columns):

        if include:
            include_list = include.split(',')
            if customer_phone_number in include_list:
                columns.append(SupportQueries.customer_phone)
            if query_text in include_list:
                columns.append(SupportQueries.query_text)
            if status in include_list:
                columns.append(SupportQueries.status)

        return columns

    def __get_expanded_columns(self, expand, customer, respondent, query_data):
        expand_list = None
        if expand:
            expand_list = [data.strip() for data in expand.split(',')]
        customer_data = self.__get_user_data(id=customer, user_type=customer_text, expand_list=expand_list)
        respondent_data = self.__get_user_data(id=respondent, user_type=respondent_text, expand_list=expand_list)
        query_data['customer'] = customer_data
        query_data['respondent'] = respondent_data
        return query_data

    def __create_links(self, offset, result_set_limit):
        links = {
            'firstPage': {
                'href': f'/support-queries?offset=0&limit={result_set_limit}'
            },
            "nextPage": {
                'href': f'/support-queries?offset={offset}&limit={result_set_limit}'
            }
        }
        if int(offset) == 0:
            links['previousPage'] = None
        else:
            links['previousPage'] = f'/support-queries?offset={int(offset) - int(result_set_limit)}' \
                                    f'&limit={result_set_limit}'

        return links

    def __get_user_data(self, id, user_type, expand_list=None):

        if id:
            if expand_list and user_type in expand_list:
                users_repository = UsersRepository()
                user_data = users_repository.fetch_by_record_id(record_id=id, now=datetime_now())
                user_data = UserSupportQueryDto(name=user_data.name, pin_code=user_data.pin_code,
                                                license_number=user_data.licence_number, email=user_data.email,
                                                phone_number=user_data.phone_number, verified=user_data.verified)
                user_data = model_to_dict(user_data)
            else:
                user_data = {}
            user_data['id'] = id
            user_data['_links'] = {
                'self': {
                    'href': f'/users/{id}'
                }
            }
            return user_data
        return {}

    def __create_clauses_on_query_fields(self, query_field, query):

        where_clauses = [SupportQueries.active]
        if query_field:
            query_fields = [data.strip() for data in query_field.split(',')]
            where_clauses = []

            for query_data in query_fields:
                where_clauses.append(SupportQueries.query_text.contains(query_data))

        where_clause_query_search = self.__create_clauses_on_query_search(query=query)
        if where_clause_query_search:
            where_clauses.append(where_clause_query_search)

        return where_clauses

    def __create_clauses_on_date_range(self, date_range):

        where_clauses = [SupportQueries.active]
        if date_range:
            date_range = date_range.split('#')
            start_date = date_range[0]
            end_date = date_range[1]
            where_clauses.append(SupportQueries.created_on >= start_date)
            where_clauses.append(SupportQueries.created_on <= end_date)

        return where_clauses

    def __create_sorting_order_and_direction(self, sort):
        sort_list = None
        if sort:
            sort_list = [data.strip() for data in sort.split(',')]
        return sort_list

    def update_raised_query(self, query_dto, query_id):
        with db_session.atomic():

            query_repository = SupportQueryRepository()

            self.validate_req_body_for_insert(query_dto=query_dto)

            support_util = SupportUtil()

            if not support_util.check_valid_email(email_id=query_dto.customer_email):
                raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Email)])

            if not support_util.check_valid_phone_number(phone_number=query_dto.customer_phone):
                raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

            query_repository.update(query_dto=query_dto, now=datetime_now(),
                                    user_id=query_dto.respondent, query_id=query_id)

            query = query_repository.find_by_id(query_id=query_id)

            context = support_util.get_query_context(
                device_token=query.customer_device_token,
                device_os_version=query.customer_device_os_version,
                app_version=query.customer_app_version,
                session_token=None
            )
            context = model_to_dict(context)
            query_status = query.status.value
            return model_to_dict(ResponseQueryDto(
                customer_email=query.customer_email,
                phone_number=query.customer_phone,
                query_text=query.query_text,
                context=context,
                status=query_status,
                query_id=query.id,
                response_date=query.response_date,
                response_comment=query.response_comment,
                customer_user=query.customer_user,
                query_date_time=query.created_on,
                respondent=query.response_by
            ))

    def __create_clauses_on_query_search(self, query):

        if query:
            where_clauses = SupportQueries.query_text.contains(query)
            return where_clauses
        return None

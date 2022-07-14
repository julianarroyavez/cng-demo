import enum

import falcon

from app.api.common import BaseResource
from app.dto.support.support_dto import QueryDto
from app.errors import AppError, UnknownError
from app.log import LOG
from app.service.support.support_service import SupportService
from app.util.support.support_util import SupportUtil

error_message_post_queries = 'failed to insert query details'
error_message_get_faqs = 'failed to fetch FAQ details'
error_message_get_queries = 'failed to fetch Active query details'
error_message_update_queries = 'failed to update query details'


class Collection(BaseResource):

    def on_post(self, req, res):
        try:
            service = SupportService()
            support_util = SupportUtil()
            LOG.info("check email")
            body = service.insert_raised_query(
                query_dto=support_util.convert_query_req_body_to_dto_for_insert(req_body=req.context['data'])
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message_post_queries,
                                                                         raw_exception=e))

    class QueryParams(enum.Enum):
        Expand = '_expand'
        Include = '_include'
        QueryField = '_query-field'
        Structure = '_structure'
        DateRange = 'date-range'
        Limit = 'limit'
        Offset = 'offset'
        Query = 'query'
        Sort = 'sort'
        Status = 'status'

        def val(self, req):
            return req.get_param(self.value)

    def on_get(self, req, res):
        try:
            service = SupportService()
            body = service.get_all_active_support_queries(
                expand=self.QueryParams.Expand.val(req),
                include=self.QueryParams.Include.val(req),
                query_field=self.QueryParams.QueryField.val(req),
                structure=self.QueryParams.Structure.val(req),
                date_range=self.QueryParams.DateRange.val(req),
                result_set_limit=self.QueryParams.Limit.val(req),
                offset=self.QueryParams.Offset.val(req),
                query=self.QueryParams.Query.val(req),
                sort=self.QueryParams.Sort.val(req),
                status=self.QueryParams.Status.val(req)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message_get_queries,
                                                                         raw_exception=e))


class UpdateCollection(BaseResource):
    def on_post(self, req, res, query_id):
        try:
            service = SupportService()
            support_util = SupportUtil()
            body = service.update_raised_query(
                query_dto=support_util.convert_query_req_body_to_dto_for_update(req_body=req.context['data']),
                query_id=query_id
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message_update_queries,
                                                                         raw_exception=e))

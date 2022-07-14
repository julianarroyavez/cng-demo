import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.service.support.support_service import SupportService

error_message_post_queries = 'failed to insert FAQ details'
error_message_get_faqs = 'failed to fetch FAQ details'
error_message_get_queries = 'failed to fetch Active query details'


class Collection(BaseResource):

    def on_get(self, req, res):
        try:
            service = SupportService()
            body = service.get_all_faqs()

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message_get_faqs,
                                                                         raw_exception=e))

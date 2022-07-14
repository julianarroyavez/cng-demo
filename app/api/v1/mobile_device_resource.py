import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.service.device_service import DeviceService


class Collection(BaseResource):
    def on_post(self, req, res):
        try:
            service = DeviceService()
            body = service.device_registration(req_body=req.context['data'], req_auth_claims=req.context['auth_claims'])

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to register device',
                                                                              raw_exception=e))

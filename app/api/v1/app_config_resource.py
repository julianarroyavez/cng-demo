import falcon

from app.api.common import BaseResource
from app.errors import UnknownError, AppError
from app.service.app_config_service import AppConfigService


class Collection(BaseResource):

    # @falcon.before(authorize, [Authorization(resource=Resources.ConfigMasters, permissions=[PermissionScopes.Search])])
    def on_get(self, req, res):
        try:
            service = AppConfigService()
            body = service.get_app_configs(after=req.params['after'])

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get app_config', raw_exception=e))

import falcon
from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.ConfigMasters, [PermissionScopes.Search])])
    def on_get(self, req, res):
        try:
            body = {}
            self.embed_entities(req, body)
            self.on_success(res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to deliver masters', raw_exception=e))

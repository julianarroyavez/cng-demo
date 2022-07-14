import falcon

from app.api.common import BaseResource
from app.domain.auth_schema import Authorization, Resources, PermissionScopes
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.charging_connector_service import ChargingConnectorService


class ItemIconImage(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.ConfigMasters, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res, connector_id):
        try:
            service = ChargingConnectorService()
            body = service.get_icon_image(charging_connector_id=connector_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body, content_type=falcon.MEDIA_PNG)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get charging connector Icon', raw_exception=e))

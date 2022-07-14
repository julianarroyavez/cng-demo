import falcon
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.vehicle_master_service import VehicleMasterService
from app.api.common import BaseResource
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.VehicleMasters, [PermissionScopes.Search])])
    def on_get(self, req, res):
        try:
            service = VehicleMasterService()
            body = service.get_vehicle_masters(req)

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get Vehicle Master', raw_exception=e))


class ItemModelImage(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.VehicleMasters, [PermissionScopes.Retrieve])])
    def on_get(self, req, res, vehicle_master_id):
        try:
            service = VehicleMasterService()
            body = service.get_vehicle_model_image(vehicle_master_id, size=req.params.get('size', None))

            self.on_image_success(res, body=body, content_type=falcon.MEDIA_PNG)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get Model Image', raw_exception=e))

import falcon

from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.vehicle_service import VehicleService
from app.api.common import BaseResource
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Vehicles, [PermissionScopes.Create])])
    def on_post(self, req, res):
        try:
            service = VehicleService()
            body = service.register_vehicle(req_body=req.context['data'],
                                            req_file=req.context['file'],
                                            req_auth_claims=req.context['auth_claims'])

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to register Vehicle',
                                                                              raw_exception=e))


class ItemVerify(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Vehicles, [PermissionScopes.Update])])
    def on_post(self, req, res, vehicle_id):
        try:
            service = VehicleService()
            body = service.verify_vehicle(req_body=req.context['data'], req_auth_claims=req.context['auth_claims'])
            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to verify vehicle',
                                                                              raw_exception=e))


class ItemCertificateImage(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Vehicles, [PermissionScopes.Retrieve])])
    def on_get(self, req, res, vehicle_id):
        try:
            service = VehicleService()
            body = service.get_vehicle_certificate_image(vehicle_id=vehicle_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get Image', raw_exception=e))


class Self(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Vehicles, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = VehicleService()
            body = service.get_user_vehicles(user_id=req.context['auth_claims'].get('user'))

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to register Vehicle', raw_exception=e))

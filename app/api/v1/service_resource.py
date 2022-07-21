import enum

import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.service_master_service import ServiceMasterService
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


class Collection(BaseResource):
    class QueryParams(enum.Enum):
        StationId = 'station'
        Type = 'type'
        Include = '_include'

    @falcon.before(authorize, [Authorization(Resources.Services, [PermissionScopes.Search])])
    def on_get(self, req, res):
        try:
            # req.params['type'] = 'amenity,cng'   # cng_delete
            filters = {
                self.QueryParams.Type.value: req.get_param(self.QueryParams.Type.value).split(",")
            }
            addons = {
                self.QueryParams.Include.value: req.get_param(self.QueryParams.Include.value).split(",")
            }

            # todo: apply station query param existence else it will provide all masters
            service = ServiceMasterService()
            body = service.get_station_services(req.get_param(self.QueryParams.StationId.value), filters, addons)

            self.on_success(res=res, status_code=falcon.HTTP_OK, body=body)
        except Exception as error:
            self.on_error(res,
                          error if isinstance(error,
                                              AppError) else UnknownError(description='failed to get nearby stations',
                                                                          raw_exception=error))


class ItemIconImage(BaseResource):

    @falcon.before(authorize,
                   [Authorization(resource=Resources.ConfigMasters, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res, service_id):
        try:
            service = ServiceMasterService()
            body = service.get_icons_of_service(service_id=service_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body, content_type=falcon.MEDIA_PNG)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get Service Icon',
                                                                              raw_exception=e))

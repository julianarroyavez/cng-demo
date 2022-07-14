import enum

import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.slot_service import SlotService
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


class Collection(BaseResource):

    class QueryParams(enum.Enum):
        Date = 'date'
        StationId = 'station'
        VehicleId = 'vehicle'
        RatedPowerId = 'rated-power'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Slots, [PermissionScopes.Search])])
    def on_get(self, req, res):
        try:
            service = SlotService()
            body = service.generate_slots(
                station_id=self.QueryParams.StationId.val(req),
                vehicle_id=self.QueryParams.VehicleId.val(req),
                date=self.QueryParams.Date.val(req),
                user_id=req.context["auth_claims"].get('user'),
                rated_power_id=self.QueryParams.RatedPowerId.val(req)
            )

            self.on_success(res=res, status_code=falcon.HTTP_OK, body=body)
        except Exception as error:
            self.on_error(res, error if isinstance(error, AppError) else UnknownError(description='failed to get nearby stations', raw_exception=error))

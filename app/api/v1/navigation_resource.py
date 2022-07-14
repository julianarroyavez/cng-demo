import enum

import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.service.navigation.navigation_service import NavigationService
from app.util.navigation.navigation_util import NavigationUtil


class Collection(BaseResource):

    class QueryParams(enum.Enum):
        Origin = 'origin'
        Destination = 'destination'

        def val(self, req):
            return req.get_param(self.value)

    def on_get(self, req, res):
        try:
            service = NavigationService()
            util = NavigationUtil()
            body = service.fetch_navigation_for_user(
                util.convert_query_params_to_navigation_object(
                    origin=self.QueryParams.Origin.val(req),
                    destination=self.QueryParams.Destination.val(req)
                )
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description="unable to fetch details",
                                                                         raw_exception=e))

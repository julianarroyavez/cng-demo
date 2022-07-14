import datetime

import falcon

from app import log
from app.api.common import BaseResource
from app.domain.auth_schema import Authorization, PermissionScopes, Resources
from app.domain.notification_schema import NotificationType
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.notification_service import NotificationService
from app.util import datetime_util

LOG = log.get_logger()


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Notifications, [PermissionScopes.Search])])
    def on_get(self, req, res):  # Notifications [search]
        params = req.params  # , limit, offset, after, type

        try:
            service = NotificationService()

            body = service.get_notification(params=params,
                                            user_id=req.context['auth_claims']['user'],
                                            device_token=req.context['auth_claims']['deviceToken'])

            self.on_success(res, status_code=falcon.HTTP_200, body=body)

        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError)
                          else UnknownError(description='Failed to get notifications',
                                            raw_exception=e))


class BulkCollection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Notifications, [PermissionScopes.Create, PermissionScopes.Update])])
    def on_post(self, req, res):
        try:
            service = NotificationService()
            body = service.update_notification(req_body=req.context['data'], req_auth_claims=req.context['auth_claims'])
            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(
                description='failed to update Notification',
                raw_exception=e))


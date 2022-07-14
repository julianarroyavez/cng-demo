import enum

import falcon

from app.domain.auth_schema import Authorization, Resources, PermissionScopes
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.rating.ratings_service import RatingsService

rating_failed = 'Failed to Update Ratings. Please try again later'


class Collection:

    @falcon.before(authorize, [Authorization(Resources.Ratings, [PermissionScopes.Create])])
    def on_post(self, req, res, data_id):
        try:
            service = RatingsService()
            body = service.save_rating(
                user_id=req.context['auth_claims'].get('user'),
                object_id=data_id,
                req_body=req.context['data'],
                attachment_one=req.context['attachmentOne'],
                attachment_two=req.context['attachmentTwo'],
                attachment_three=req.context['attachmentThree']

            )
            self.embed_entities(req=req, res_body=body)

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=rating_failed,
                                                                              raw_exception=e))

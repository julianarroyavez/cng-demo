import enum

import falcon
from app import log
from app.errors import AppError, UnknownError
from app.api.common import BaseResource
from app.hooks.authorization_hook import authorize
from app.service.rating.ratings_service import RatingsService
from app.service.station_service import StationService
from app.domain.auth_schema import Resources, PermissionScopes, Authorization


LOG = log.get_logger()
rating_upload_failed = 'Failed to Update Ratings. Please try again later.'
rating_failed = 'Failed to fetch Reviews for this station. Please try again later.'


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Stations, [PermissionScopes.Search])])
    def on_get(self, req, res):  # stations [search]
        params = req.params  # , nearby, latitude, longitude
        if 'nearby' in params:
            try:
                service = StationService()
                params['charging-type'] = 'CNG'
                body = service.get_nearby_stations(params=params)

                self.on_success(res, status_code=falcon.HTTP_200, body=body)
            except Exception as e:
                self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get nearby stations',
                                                                                  raw_exception=e))

    @falcon.before(authorize, [Authorization(Resources.Stations, [PermissionScopes.Retrieve, PermissionScopes.Create])])
    def on_post(self, req, res):
        try:
            service = StationService()
            body = service.evso_registration(req_body=req.context['data'],
                                             thumbnail_file=req.context['thumbnail-file'],
                                             file1=req.params.get('file1', None), file2=req.params.get('file2', None),
                                             file3=req.params.get('file3', None), file4=req.params.get('file4', None),
                                             req_auth_claims=req.context['auth_claims'])
            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to register station', raw_exception=e))


class ItemImage(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Stations, [PermissionScopes.Retrieve])])
    def on_get(self, req, res, station_id, image_id):
        try:
            service = StationService()
            body = service.get_station_image(station_id=station_id, image_id=image_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get Image', raw_exception=e))


class RatingCollection(BaseResource):

    class QueryParams(enum.Enum):
        limit = 'limit'
        offset = 'offset'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Ratings, [PermissionScopes.Create])])
    def on_post(self, req, res, station_id):
        try:
            service = RatingsService()
            body = service.save_rating(
                user_id=req.context['auth_claims'].get('user'),
                object_id=station_id,
                req_body=req.context['data'],
                attachment_one=req.context.get('attachmentOne', None),
                attachment_two=req.context.get('attachmentTwo', None),
                attachment_three=req.context.get('attachmentThree', None),
                is_station=True
            )
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=rating_upload_failed,
                                                                              raw_exception=e))

    @falcon.before(authorize, [Authorization(Resources.Ratings, [PermissionScopes.Retrieve])])
    def on_get(self, req, res, station_id):
        try:
            service = RatingsService()
            body = service.fetch_station_ratings(
                station_id=station_id,
                limit=self.QueryParams.limit.val(req),
                offset=self.QueryParams.offset.val(req)
            )

            self.on_image_success(res=res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=rating_failed,
                                                                              raw_exception=e))

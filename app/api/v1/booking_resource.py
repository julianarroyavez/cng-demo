import enum

import falcon

from app.api.common import BaseResource
from app.constant import dashboard_constant
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.log import LOG
from app.service.booking_service import BookingService
from app.domain.auth_schema import Resources, PermissionScopes, Authorization
from app.service.rating.ratings_service import RatingsService
from app.service.evso_booking_service import EVSOBookingService

booking_failed = 'failed to process booking'
auth_claims = 'auth_claims'


rating_failed = 'Failed to Update Ratings. Please try again later'


class Collection(BaseResource):

    class QueryParams(enum.Enum):
        DateRange = 'date-range'
        Offset = 'offset'
        Limit = 'limit'
        IncludeParams = '_include'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Bookings, [PermissionScopes.Create])])
    def on_post(self, req, res):
        try:
            service = BookingService()

            body = service.process_booking(
                user_id=req.context['auth_claims'].get('user'),
                device_token=req.context['auth_claims'].get('deviceToken'),
                booking_req=req.context['data']
            )
            self.embed_entities(req=req, res_body=body)

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=booking_failed,
                                                                              raw_exception=e))

    @falcon.before(authorize, [Authorization(resource=Resources.Bookings, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = BookingService()
            evso_booking_service = EVSOBookingService()

            if self.QueryParams.DateRange.val(req):
                LOG.info(req)
                LOG.info(req.params)
                try:
                    include_params = self.QueryParams.IncludeParams.val(req).split(',')
                except Exception:
                    include_params = None
                date_range = self.QueryParams.DateRange.val(req).split('#')
                start_date = date_range[0]
                end_date = date_range[1]
                body = evso_booking_service.get_evso_station_bookings(
                    start_date=start_date,
                    end_date=end_date,
                    station_record_id=req.context[auth_claims].get(dashboard_constant.STATION_ID, None),
                    device_token=req.context[auth_claims].get('deviceToken'),
                    offset=self.QueryParams.Offset.val(req),
                    limit=self.QueryParams.Limit.val(req),
                    include_params=include_params
                )
            else:
                body = service.get_list_of_bookings(
                    user_id=req.context[auth_claims].get('user'),
                    offset=req.params['offset'],
                    limit=req.params['limit']
                )

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=
                                                                              'failed to get list of booking details',
                                                                              raw_exception=e))


class Item(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Bookings, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res, booking_id):
        try:
            service = BookingService()
            body = service.get_booking_details(
                booking_id=booking_id
            )

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=
                                                                              'failed to get booking details',
                                                                              raw_exception=e))


class CancelBooking(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Bookings, [PermissionScopes.Update])])
    def on_post(self, req, res, booking_id):
        try:
            service = BookingService()
            body = service.cancel_booking(
                user_id=req.context['auth_claims'].get('user'),
                booking_id=booking_id,
                device_token=req.context['data']['context']['deviceToken']
            )
            self.embed_entities(req=req, res_body=body)
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=booking_failed,
                                                                              raw_exception=e))


class CancelBookingPenalties(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Bookings, [PermissionScopes.Retrieve])])
    def on_get(self, req, res, booking_id):
        try:
            service = BookingService()
            body = service.get_cancellation_confirmation(booking_id=booking_id)
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=booking_failed,
                                                                              raw_exception=e))


class RatingCollection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Ratings, [PermissionScopes.Create])])
    def on_post(self, req, res, booking_id):
        try:
            service = RatingsService()
            body = service.save_rating(
                user_id=req.context['auth_claims'].get('user'),
                object_id=booking_id,
                req_body=req.context['data'],
                attachment_one=req.context.get('attachmentOne', None),
                attachment_two=req.context.get('attachmentTwo', None),
                attachment_three=req.context.get('attachmentThree', None)

            )
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=rating_failed,
                                                                              raw_exception=e))


class NotificationPopupCollection(BaseResource):

    class QueryParams(enum.Enum):
        hygge_box_number = 'hygge-box-number'

        def val(self, req):
            return req.get_param(self.value)

    def on_get(self, req, res, booking_id):
        try:
            LOG.info('Booking resource %s' % booking_id)
            service = BookingService()
            body = service.send_booking_popup_to_topic(
                booking_id=booking_id,
                hygge_box_number=self.QueryParams.hygge_box_number.val(req)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)

        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description=
                                                                              'failed to get booking details',
                                                                              raw_exception=e))

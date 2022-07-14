from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.util.datetime_util import datetime_now
from app.handlers.notification.booking_handler import BookingHandler
from app.handlers.notification.payment_handler import PaymentHandler
from app.handlers.notification.user_handler import UserHandler
from app.handlers.notification.vehicle_handler import VehicleHandler


class NotificationFactory:

    def create_and_queue_notification(self, data, user_id, device_token, trigger, device, optional_data=None):

        if device is None:
            mobile_devices_repository = MobileDevicesRepository()
            if device_token is not None:
                device = mobile_devices_repository.fetch_by_device_token(device_token=device_token, now=datetime_now())

        if trigger == 'Booking_confirmation':
            booking_handler = BookingHandler()
            notification = booking_handler.create_booking_notification(booking=data, user_id=user_id, device=device)
        elif trigger == 'Booking_cancellation':
            booking_handler = BookingHandler()
            notification = booking_handler.create_booking_cancellation_notification(booking_data=data, user_id=user_id,
                                                                                    device=device,
                                                                                    booking_station_name=
                                                                                    optional_data[
                                                                                        'booking_station_name'])
        elif trigger == 'Booking_rejection':
            booking_handler = BookingHandler()
            notification = booking_handler.create_booking_rejection_notification(booking_data=data, user_id=user_id,
                                                                                 device=device)
        elif trigger == 'Token_transfer_receiver':
            payment_handler = PaymentHandler()
            notification = payment_handler.create_token_transfer_notification(payment_data=data, user_id=user_id,
                                                                              device=device)
        elif trigger == 'Token_add':
            payment_handler = PaymentHandler()
            notification = payment_handler.create_token_add_notification(token_data=data, user_id=user_id,
                                                                         device=device)
        elif trigger == 'Token_failed':
            payment_handler = PaymentHandler()
            notification = payment_handler.create_token_failed_notification(token_data=data, user_id=user_id,
                                                                            device=device)
        elif trigger == 'Vehicle_added':
            vehicle_handler = VehicleHandler()
            notification = vehicle_handler.create_vehicle_addition_notification(vehicle_data=data, user_id=user_id,
                                                                                device=device)
        elif trigger == 'Vehicle_verified':
            vehicle_handler = VehicleHandler()
            notification = vehicle_handler.create_vehicle_verification_notification(vehicle_data=data, user_id=user_id,
                                                                                    device=device)
        elif trigger == 'User_verified':
            user_handler = UserHandler()
            notification = user_handler.create_user_verification_notification(user_data=data, user_id=user_id,
                                                                              device=device, device_token=None)
        elif trigger == 'Login':
            user_handler = UserHandler()
            notification = user_handler.create_user_login_notification(user_data=data, user_id=user_id,
                                                                       fcm_token=optional_data['fcm_token'])
        return notification

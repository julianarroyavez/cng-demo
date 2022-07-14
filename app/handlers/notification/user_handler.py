import datetime

from pytz import timezone

from app.domain.notification_schema import Notifications, NotificationEvent, Action
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.service.notification_service import NotificationService
from app.util.datetime_util import datetime_now, date_to_ist_format
from app.util.notification_util import NotificationUtil


class UserHandler:

    def create_user_verification_notification(self, user_data, user_id, device, device_token):

        mobile_devices_repository = MobileDevicesRepository()
        notification_util = NotificationUtil()

        if device is None:
            device = mobile_devices_repository.fetch_by_device_token(device_token=device_token, now=datetime_now())

        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.UserVerification
        notification.event_time = datetime.datetime.utcnow()
        if user_data.verified is not None:
            if user_data.verified:
                value = 'VERIFIED'
            else:
                value = 'REJECTED'
        replaceable_value = [value]
        title_obj = NotificationEvent.get_title_and_message_for_user(string=NotificationEvent.UserVerification.value,
                                                                     replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(user_data.record_id), "resource": "User"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

    def create_user_login_notification(self, user_data, user_id, fcm_token):
        notification_util = NotificationUtil()

        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.UserLogin
        notification.event_time = user_data.created_on
        now_utc = datetime.datetime.now(timezone('UTC'))
        replaceable_value = [str(date_to_ist_format(now_utc.astimezone(timezone('Asia/Kolkata'))))]
        title_obj = NotificationEvent.get_title_and_message_for_user(string=NotificationEvent.UserLogin.value,
                                                                     replaceable_value=replaceable_value)

        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.linked_resource = {"resource_id": str(user_id), "resource": "User"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": fcm_token
        }
        return send_notification

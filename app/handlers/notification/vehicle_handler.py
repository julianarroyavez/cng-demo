import datetime
import uuid

from app.domain.notification_schema import Notifications, NotificationEvent, Action
from app.log import LOG
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.service.notification_service import NotificationService
from app.util.datetime_util import datetime_now
from app.util.deep_link_util import DeepLinkCreation
from app.util.notification_util import NotificationUtil


class VehicleHandler:

    def create_vehicle_verification_notification(self, vehicle_data, user_id, device):
        LOG.info('inside vehicle verification')
        notification_util = NotificationUtil()

        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.VehicleVerification
        notification.event_time = datetime.datetime.utcnow()
        if vehicle_data.verified is not None:
            if vehicle_data.verified:
                value = 'VERIFIED'
            else:
                value = 'REJECTED'
        replaceable_value = [value]
        title_obj = NotificationEvent.get_title_and_message_for_user(string=NotificationEvent.VehicleVerification.value,
                                                                     replaceable_value=replaceable_value)

        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value

        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(vehicle_data.id), "resource": "Vehicle"}

        notification.generated_on = datetime_now()

        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

    def create_vehicle_addition_notification(self, vehicle_data, user_id, device):
        notification_util = NotificationUtil()
        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.VehicleAddition
        notification.event_time = vehicle_data.created_on
        title_obj = NotificationEvent.get_title_and_message_for_user(string=NotificationEvent.VehicleAddition.value,
                                                                     replaceable_value=None)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": uuid.UUID(vehicle_data.id).hex, "resource": "Vehicle"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)

        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

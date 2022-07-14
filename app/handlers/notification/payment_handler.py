import datetime

from app.domain.notification_schema import Notifications, NotificationEvent, Action
from app.log import LOG
from app.repository.users_repository import UsersRepository
from app.service.notification_service import NotificationService
from app.util.datetime_util import datetime_now
from app.util.notification_util import NotificationUtil


class PaymentHandler:

    def create_token_transfer_notification(self, payment_data, user_id, device):

        token_data = payment_data['payment']
        sender_id = payment_data['sender_id']
        user_repository = UsersRepository()
        notification_util = NotificationUtil()
        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.TxnTransferToken
        notification.event_time = datetime.datetime.utcnow()
        try:
            sender = user_repository.fetch_by_record_id(record_id=token_data.sender, now=datetime_now())
        except Exception:
            sender = user_repository.fetch_by_record_id(record_id=sender_id, now=datetime_now())

        replaceable_value = [str(round(token_data.order_amount, 2)), str(sender.phone_number)]
        title_obj = NotificationEvent.get_title_and_message_for_payment(string=NotificationEvent.TxnTransferToken.value,
                                                                        replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(token_data.id), "resource": "Payment"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

    def create_token_add_notification(self, token_data, user_id, device):
        notification_util = NotificationUtil()

        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.TxnAddToken
        notification.event_time = datetime.datetime.utcnow()
        replaceable_value = [str(round(token_data.order_amount))]
        title_obj = NotificationEvent.get_title_and_message_for_payment(string=NotificationEvent.TxnAddToken.value,
                                                                        replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(token_data.id), "resource": "Payment"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

    def create_token_failed_notification(self, token_data, user_id, device):
        notification_util = NotificationUtil()

        notifications = []

        notification = Notifications()
        notification.event = NotificationEvent.TxnTransferFailedToken
        notification.event_time = datetime.datetime.utcnow()
        title_obj = NotificationEvent.get_title_and_message_for_payment(
            string=NotificationEvent.TxnTransferFailedToken.value,
            replaceable_value=None)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(token_data.id), "resource": "Payment"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)
        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

from app import log, config
from app.domain.notification_schema import Notifications, NotificationEvent, NotificationType
from app.repository.app_configs_repository import AppConfigRepository
from app.repository.notification_repository import NotificationRepository
from app.util import datetime_util
from app.util.datetime_util import datetime_now
from app.util.mqtt_publisher import send_notification
from app.util.notification_util import NotificationUtil

LOG = log.get_logger()

get_params_for_null_values = {
    "offset": 0,
    "limit": 50,
    "type": NotificationType.BothBellAndBar.value,
    "after": datetime_util.get_minimum_date_value()
}


class NotificationService:

    def get_notification(self, params, user_id, device_token):
        notification_repository = NotificationRepository()

        app_configs_repository = AppConfigRepository()
        notification_util = NotificationUtil()

        params = notification_util.set_params_for_null_values(params=params, callback_params=get_params_for_null_values)

        if params['type'] == NotificationType.NotificationBar.value:
            type_config = app_configs_repository.fetch_notification_bar_events(now=datetime_now())
        elif params['type'] == NotificationType.BellIcon.value:
            type_config = app_configs_repository.fetch_notification_bell_icon_events(now=datetime_now())
        else:
            type_config = app_configs_repository.fetch_all_notification_events(now=datetime_now())

        type_configs = list(type_config.split(','))
        notification_types = []
        for notification_type in type_configs:
            notification_types.append(NotificationEvent.from_str(notification_type))

        columns = [Notifications.id, Notifications.event, Notifications.event_time, Notifications.data]
        notifications = notification_repository.fetch_all_by_user(columns=columns, user_id=user_id,
                                                                  offset=params['offset'], limit=params['limit'],
                                                                  after=params['after'], type_configs=notification_types)
        LOG.info(notifications)
        result = notification_util.create_notification_json_data(notifications=notifications)
        LOG.info(result)
        return result

    def update_notification(self, req_body, req_auth_claims):
        LOG.info('inside update Notification service')
        notification_repository = NotificationRepository()
        notification_util = NotificationUtil()

        notifications = req_body['notifications']
        result = []
        if notifications is not None:
            for notification in notifications:
                if notification['id'] is not None:
                    try:
                        notification_from_db = notification_repository.fetch_by_id(notification_id=notification['id'])
                        notification_to_be_updated = self.__set_data_to_update_notification(notification_req=notification,
                                                                                            notification_from_db=notification_from_db)
                        notification_repository.update_record(record=notification_to_be_updated)
                        result.append(notification_to_be_updated)
                    except Exception as e:
                        LOG.error('Failed to update Notification due to error: %s' % e)

        return notification_util.create_notification_post_json_data(notifications=result)

    def __set_data_to_update_notification(self, notification_req, notification_from_db):

        LOG.info('notification req : %s' % notification_req)

        notification_from_db.event = NotificationEvent.from_str(notification_req['event'])
        notification_from_db.received_on = notification_req['receivedOn']
        if notification_req.get('displayedOn') is not None:
            notification_from_db.displayed_on = notification_req['displayedOn']

        if notification_req.get('engagedOn') is not None:
            notification_from_db.engaged_on = notification_req['engagedOn']

        if notification_req.get('engagedSource') is not None:
            notification_from_db.engaged_source = notification_req['engagedSource']

        if notification_req.get('engagedAction') is not None:
            notification_from_db.engaged_action = notification_req['engagedAction']

        notification_from_db.modified_on = datetime_now()

        return notification_from_db

    def insert_notification(self, notifications, to_device):

        notification_repository = NotificationRepository()
        notification_util = NotificationUtil()

        for notification in notifications:
            notification_data = notification_repository.insert(notification=notification,
                                                               user_id=notification.recipient,
                                                               mobile_id=notification.recipient_device)

            data = notification_util.create_notification_content_dict(notification=notification_data,
                                                                      scheduled_time=notification.event_time,
                                                                      to_device=to_device)
            new_data = notification_data.data
            new_data['id'] = data['data']['id']
            notification_repository.update_notification_json_object(notification_id=notification_data.id, data=new_data)
            self.__send_notification_to_topic(notification=data)

    def __send_notification_to_topic(self, notification):
        try:
            event_topic_name = config.TOPIC['notification_event']
            alert_topic_name = config.TOPIC['notification_alert']
            popup_topic_name = config.TOPIC['notification_popup']
            application_name = config.TOPIC['application_name']
            topic = alert_topic_name

            if notification['data']['notificationType'] == NotificationType.BellIcon.value:
                topic = event_topic_name
            elif notification['data']['notificationType'] == NotificationType.Popup.value:
                topic = popup_topic_name

            send_notification(topic_name=topic, application_name=application_name,
                              notification=notification)
        except Exception as e:
            LOG.error("Failed to push notification in queue")
            LOG.error(e)

    def update_cancelled_notification(self, resource_id, events):
        notification_repository = NotificationRepository()
        notification_repository.update_notification_cancelled_time(resource_id=resource_id, now=datetime_now(),
                                                                   events=events)

    def send_notification_popup_to_topic(self, notification):
        try:
            topic = config.TOPIC['notification_popup']
            application_name = config.TOPIC['application_name']
            send_notification(topic_name=topic, application_name=application_name,
                              notification=notification)
        except Exception as e:
            LOG.error("Failed to push notification in queue")
            LOG.error(e)

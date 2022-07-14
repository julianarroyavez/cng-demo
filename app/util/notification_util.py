from app.domain.notification_schema import Action, NotificationType
from app.log import LOG
from app.repository.app_configs_repository import AppConfigRepository
from app.util.datetime_util import datetime_now, date_format
from app.util.deep_link_util import DeepLinkCreation


class NotificationUtil:

    def create_single_notification_json_data(self, notification, title_obj):
        deep_link = DeepLinkCreation()
        app_config_repository = AppConfigRepository()
        deep_link_events = app_config_repository.fetch_all_notification_events_for_deep_link(now=datetime_now())
        deep_link_url = deep_link.create_deep_link(notification=notification, deep_link_events=deep_link_events)
        result = {
            "id": notification.id,
            "event": notification.event.value,
            "eventTime": date_format(notification.event_time.utcnow()),
            "title": title_obj['title'],
            "message": title_obj['message']
        }
        actions = []
        if deep_link_url is not None:
            entry = {
                "action": Action.Click.value,
                "actionDeepLink": deep_link_url
            }
            actions.append(entry)
            result['actions'] = actions
        return result

    def create_notification_json_data(self, notifications):
        result = {
            "notifications": []
        }
        result_list = []
        for notification in notifications:
            result_list.append(notification.data)
        result['notifications'] = result_list
        return result

    def set_params_for_null_values(self, params, callback_params):
        if params.get('offset') is None:
            params['offset'] = callback_params['offset']
        if params.get('limit') is None:
            params['limit'] = callback_params['limit']
        if params.get('type') is None:
            params['type'] = callback_params['type']
        if params.get('after') is None:
            params['after'] = callback_params['after']
        return params

    def create_notification_post_json_data(self, notifications):
        result = {
            "notifications": []
        }
        result_list = []
        for notification in notifications:
            res = {
                "id": notification.data['id']
            }
            result_list.append(res)
        result['notifications'] = result_list
        return result

    def create_notification_content_dict(self, notification, scheduled_time, to_device):
        deep_link = DeepLinkCreation()
        app_config_repository = AppConfigRepository()
        deep_link_events = app_config_repository.fetch_all_notification_events_for_deep_link(now=datetime_now())
        scheduled_notifications = app_config_repository.fetch_all_notification_scheduled_events(now=datetime_now())
        deep_link_url = deep_link.create_deep_link(notification=notification, deep_link_events=deep_link_events)
        notification_type = self.__get_notification_type(event_name=notification.event.value)
        result = {
            "to": to_device,
            "data": {
                "id": notification.id,
                "event": notification.event.value,
                "eventTime": date_format(notification.event_time.utcnow()),
                "title": notification.data['title'],
                "message": notification.data['message'],
                "engagedSource": notification.engaged_source,
                "notificationType": notification_type
            }
        }
        if scheduled_notifications is not None and notification.event.value in scheduled_notifications:
            result['data']['isScheduled'] = True
            result['data']['scheduledTime'] = scheduled_time.isoformat()
        if deep_link_url is not None:
            actions = []
            entry = {
                "action": Action.Click.value,
                "actionDeepLink": deep_link_url
            }
            actions.append(entry)
            result['data']['actions'] = actions
        return result

    def __get_notification_type(self, event_name):
        app_configs_repository = AppConfigRepository()
        bell = False
        bar = False
        type_config = app_configs_repository.fetch_notification_bar_events(now=datetime_now())
        if event_name in type_config:
            bar = True
        type_config = app_configs_repository.fetch_notification_bell_icon_events(now=datetime_now())
        if event_name in type_config:
            bell = True
        if bell and not bar:
            return NotificationType.BellIcon.value
        elif bar and not bell:
            return NotificationType.NotificationBar.value
        return NotificationType.BothBellAndBar.value

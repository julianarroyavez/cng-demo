import json

from app import config
from app.repository.app_configs_repository import AppConfigRepository
from app.util.datetime_util import datetime_now


class DeepLinkCreation:

    def create_action_deep_link_url(self, screen, source, object_id, action):
        id_in_string = str(object_id)
        url = config.DEEP_LINK['url'].replace("[screen]", screen).replace("[source]", source). \
            replace("[action]", action).replace("[id]", id_in_string)
        return url

    def create_deep_link(self, notification, deep_link_events):

        if notification.event.value in deep_link_events:

            screens = json.loads(deep_link_events)
            for screen, event in screens.items():
                if notification.event.value in event:
                    url = self.create_action_deep_link_url(screen=screen, source=notification.engaged_source,
                                                           action=notification.engaged_action,
                                                           object_id=notification.linked_resource['resource_id'])
                    return url
        return None

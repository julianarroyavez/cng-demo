import enum
from datetime import datetime
from app.util.datetime_util import datetime_now
from app.repository.app_configs_repository import AppConfigRepository


class AppConfigService:
    class Links(enum.Enum):
        Next = '/api/v1/app-configs?after={key}'

        def href(self, key):
            return self.value.format(**dict(key=key))

    def get_app_configs(self, after):
        app_config_repository = AppConfigRepository()
        app_configs = []

        value_from = datetime.strptime(after, '%y-%m-%dT%H:%M:%S.%f')
        value_till = datetime_now()

        for app_config in app_config_repository.fetch_all__visibility_public_after_time(value_from=value_from,
                                                                                        now=value_till):
            app_configs.append(
                {
                    "id": app_config.record_id,
                    "key": app_config.key,
                    "value": app_config.value
                }
            )

        value_till = datetime.strptime(value_till, '%Y-%m-%dT%H:%M:%S.%f').strftime('%y-%m-%dT%H:%M:%S.%f')
        return {
            "valuesFrom": after,
            "valuesTill": value_till,
            "appConfigs": app_configs,
            "_links": {
                "next": {
                    "href": self.Links.Next.href(key=value_till)
                }
            }
        }

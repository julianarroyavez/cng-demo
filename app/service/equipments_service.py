import enum

from app.domain.auth_schema import AppConfigs
from app.repository.app_configs_repository import AppConfigRepository
from app.repository.equipment_type_masters_repository import EquipmentTypeMasterRepository
from app.util.datetime_util import datetime_now


class EquipmentTypeMasterService:
    class Links(enum.Enum):
        IconImage = '/api/v1/equipment-type-masters/{icon_id}/icon-image'

        def href(self, icon_id):
            return self.value.format(**dict(icon_id=icon_id))

    def embed_equipment_types(self, root_body, user_id, params):
        now = datetime_now()
        equipment_list = []
        app_configs_list = []

        app_configs_repository = AppConfigRepository()
        equipments_repository = EquipmentTypeMasterRepository()
        equipments = equipments_repository.fetch_all(now=now)

        for equipment in equipments:
            equipment_list.append({
                "id": equipment.record_id,
                "name": equipment.name,
                "type": equipment.type.value,
                "iconImage": {
                    "href": self.Links.IconImage.href(icon_id=equipment.record_id)
                },
                "rank": equipment.rank,
                "active": equipment.active
            })

        equipment_type_masters = {
            'equipmentTypeMasters': equipment_list
        }
        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['equipmentTypeMasters'] = equipment_type_masters.pop('equipmentTypeMasters')

        if 'app-configs.key' in params:
            key_list = params['app-configs.key'].split(",")
            where_clauses = []

            for key in key_list:
                where_clauses.append(AppConfigs.key == key)

            app_configs = app_configs_repository.fetch_by_keys(where_clauses=where_clauses, now=datetime_now())

            for app_config in app_configs:
                app_configs_list.append({
                    "id": app_config.id,
                    "key": app_config.key,
                    "value": app_config.value
                })

            if root_body.get('_embedded', None) is None:
                root_body['_embedded'] = {
                    'appConfigs': app_configs_list
                }
            else:
                root_body['_embedded']['appConfigs'] = app_configs_list
            return root_body

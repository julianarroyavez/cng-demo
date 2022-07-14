import enum

from app.repository.charging_connectors_repository import ChargingConnectorsRepository
from app.util import image_util
from app.util.datetime_util import datetime_now


class ChargingConnectorService:
    class Links(enum.Enum):
        IconImage = '/api/v1/charging-connectors/{key}/icon-image'

        def href(self, key):
            return self.value.format(**dict(key=key))

    def embed_charging_connectors(self, root_body, user_id, params):
        connectors = ChargingConnectorsRepository().fetch_all(now=datetime_now())

        embed_list = []
        for connector in connectors:
            embed_list.append({
                "id": connector.record_id,
                "name": connector.name,
                "standardName": connector.standard_name,
                "iconImage": {
                    "href": self.Links.IconImage.href(key=connector.record_id)
                },
                "rank": 1
            })

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['chargingConnectors'] = embed_list

    def get_icon_image(self, charging_connector_id, size=None):
        charging_connector_repository = ChargingConnectorsRepository()
        image = charging_connector_repository.fetch_icon_image_by_id(record_id=charging_connector_id, now=datetime_now())

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

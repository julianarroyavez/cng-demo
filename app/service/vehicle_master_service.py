import enum

from app.domain.resource_schema import VehicleMasters
from app.errors import FileNotExistsError
from app.log import LOG
from app.repository.charging_connectors_repository import ChargingConnectorsRepository
from app.repository.vehicle_masters_repository import VehicleMastersRepository
from app.util import image_util
from app.util.datetime_util import datetime_now


class VehicleMasterService:
    class Links(enum.Enum):
        ModelImage = '/api/v1/vehicle-masters/{vehicle_master_id}/model-image'
        IconImage = '/api/v1/charging-connectors/{vehicle_master_id}/icon-image'

        def href(self, vehicle_master_id):
            return self.value.format(**dict(vehicle_master_id=vehicle_master_id))

    def get_vehicle_masters(self, req):
        vehicle_masters_repository = VehicleMastersRepository()

        objects_list = []

        columns = [VehicleMasters.record_id, VehicleMasters.brand, VehicleMasters.model,
                   VehicleMasters.manufacturing_year, VehicleMasters.charging_connector_records]

        for vehicle_master in vehicle_masters_repository.fetch_all(columns=columns, now=datetime_now()).dicts():
            vehicle_master['id'] = vehicle_master.pop('record_id')
            vehicle_master['maker'] = vehicle_master.pop('brand')
            vehicle_master['manufacturingYear'] = vehicle_master.pop('manufacturing_year')
            vehicle_master['modelImage'] = {
                'href': self.Links.ModelImage.href(vehicle_master_id=vehicle_master['id'])
            }
            LOG.info('assign all charging connectors')
            vehicle_master['chargingConnectors'] = vehicle_master.pop('charging_connector_records')
            connector_list = []
            LOG.info('Fetch all charging connectors')
            charging_connector = ChargingConnectorsRepository().fetch_all_by_ids(
                ids=vehicle_master.get('chargingConnectors'),
                now=datetime_now()
            )
            LOG.info('Loops all charging connectors')
            LOG.info(charging_connector)
            for connector in charging_connector:
                LOG.info(connector)
                connector_list.append({
                    "id": connector.record_id,
                    "name": connector.name,
                    "standardName": connector.standard_name,
                    "iconImage": {
                        "href": self.Links.IconImage.href(vehicle_master_id=connector.record_id)
                    },
                    "rank": 1
                })
            LOG.info('map all charging connectors')
            LOG.info(connector_list)
            vehicle_master['chargingConnectors'] = connector_list

            objects_list.append(vehicle_master)

        return {
            'vehicleMasters': objects_list
        }

    def get_vehicle_model_image(self, vehicle_master_id, size=None):
        vehicle_masters_repository = VehicleMastersRepository()
        image = vehicle_masters_repository.fetch_model_image_by_id(vehicle_master_id=vehicle_master_id, now=datetime_now())
        if image is None:
            raise FileNotExistsError(description="data not found")

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

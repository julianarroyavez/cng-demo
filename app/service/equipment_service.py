from app.database import db_session
from app.domain.resource_schema import Chargers
from app.log import LOG
from app.domain.auth_schema import EquipmentTypes
from app.errors import InvalidParameterError, MissingFieldError, FieldErrors, ConflictParameterError, InvalidFieldError, \
    ErrorMessages
from app.repository.app_configs_repository import AppConfigRepository
from app.repository.chargers_repository import ChargersRepository
from app.repository.equipment_type_masters_repository import EquipmentTypeMasterRepository
from app.repository.equipments_repository import EquipmentsRepository
from app.repository.nozzles_repository import NozzlesRepository
from app.repository.service_rates_repository import ServiceRatesRepository
from app.repository.station_services_repository import StationServicesRepository
from app.util import image_util, string_util
from app.util.datetime_util import datetime_now


class EquipmentService:
    def embed_equipments(self, root_body, user_id, params):
        equipments_repository = EquipmentsRepository()
        equipment_type = EquipmentTypes.from_str(params.get('equipment-type'))
        equipments_list = []

        columns = [Chargers.id, Chargers.type, Chargers.serial_id, Chargers.product_id, Chargers.model_id,
                   Chargers.asset_id, Chargers.name, Chargers.rank, Chargers.station_record]
        equipments = equipments_repository.fetch_all_by_type_and_station_id(columns=columns, user_id=user_id,
                                                                            equipment_type=equipment_type,
                                                                            now=datetime_now())

        for equipment in equipments:
            equipments_list.append({
                "chargerId": equipment.chargers.id,
                "type": equipment.chargers.type.value,
                "serialId": equipment.chargers.serial_id,
                "productId": equipment.chargers.product_id,
                "modelId": equipment.chargers.model_id,
                "assetId": equipment.chargers.asset_id,
                "name": equipment.chargers.name,
                "rank": equipment.chargers.rank,
                "station": {
                    "id": equipment.chargers.station_record
                }
            })
        if root_body.get('_embedded', None) is None:
            root_body['_embedded'] = {
                'equipments': equipments_list
            }
        else:
            root_body['_embedded']['equipments'] = equipments_list
        return root_body

    def validate_equipments_addition_chargers_request(self, req_body, max_nozzle_guns_value):
        if len(req_body['nozzles']) > max_nozzle_guns_value:
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.MaxConnector.value.format(**dict(max_nozzle_guns_value=max_nozzle_guns_value)),
                field=FieldErrors.Nozzles)])

        if "nozzles" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.Nozzles)])

        if "type" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.ChargerType)])

        if not string_util.check_if_alphanumeric(req_body['type']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.ChargerType)])

        if "serialId" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.ChargersSerialId)])

        if not string_util.check_if_alphanumeric(req_body['serialId']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.ChargersSerialId)])

        if "name" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.ChargersName)])

        name = req_body['name'].replace(' ', '')
        if not string_util.check_if_alphanumeric(name):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.ChargersName)])

        if "rank" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.ChargersRank)])

        if "id" not in req_body["station"]:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.StationId)])

    def validate_equipments_addition_nozzles_request(self, req_body):
        if "id" not in req_body["chargingConnector"]:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.ChargingConnectorId)])

        if "id" not in req_body["ratedPower"]:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.RatedPowerId)])

        if "serialId" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.NozzlesSerialId)])

        if not string_util.check_if_alphanumeric(req_body['serialId']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.NozzlesSerialId)])

        if "name" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.NozzlesName)])

        name = req_body['name'].replace(' ', '')
        if not string_util.check_if_alphanumeric(name):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.NozzlesName)])

        if "rank" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.NozzlesRank)])

    def equipments_addition(self, req_body, req_auth_claims):
        app_configs_repository = AppConfigRepository()
        max_nozzle_guns_value = app_configs_repository.fetch_max_nozzle_guns_in_one_charger(now=datetime_now())

        LOG.info('max_nozzle_guns_value %s' % max_nozzle_guns_value)

        added_chargers = []
        nozzle_list = []

        nozzles_repository = NozzlesRepository()
        chargers_repository = ChargersRepository()
        equipments_repository = EquipmentsRepository()
        station_services_repository = StationServicesRepository()
        service_rates_repository = ServiceRatesRepository()

        with db_session.atomic():

            for charger in req_body['chargers']:
                self.validate_equipments_addition_chargers_request(req_body=charger,
                                                                   max_nozzle_guns_value=max_nozzle_guns_value)

                try:
                    equipment_type = EquipmentTypes.from_str(string=charger['type'])
                except Exception:
                    EquipmentTypes.from_str(string=req_body['type'])

                serial_id = charger.get('serialId')
                product_id = charger.get('productId')
                model_id = charger.get('modelId')
                asset_id = charger.get('assetId')
                charger_name = charger['name']
                charger_rank = charger['rank']
                station_id = charger['station']['id']

                newly_added_equipment = equipments_repository.insert(equipment_type=equipment_type, serial_id=serial_id,
                                                                     product_id=product_id, model_id=model_id,
                                                                     asset_id=asset_id, req_auth_claims=req_auth_claims)

                newly_added_charger = chargers_repository.insert(charger_name=charger_name, charger_rank=charger_rank,
                                                                 station_id=station_id, req_auth_claims=req_auth_claims,
                                                                 equipment_type=equipment_type, serial_id=serial_id,
                                                                 product_id=product_id, model_id=model_id,
                                                                 asset_id=asset_id, record_id=newly_added_equipment.id)

                for nozzle in charger['nozzles']:

                    self.validate_equipments_addition_nozzles_request(req_body=nozzle)

                    charging_connector_id = nozzle['chargingConnector']['id']
                    rated_power_id = nozzle['ratedPower']['id']
                    nozzle_serial_id = nozzle.get('serialId')
                    nozzle_asset_id = nozzle.get('assetId')
                    nozzle_rank = nozzle['rank']
                    connector_name = nozzle['name']

                    serial_id_list = [t.serial_id for t in
                                      nozzles_repository.fetch_serial_id_by_station_id_and_charger_id(
                                          station_id=station_id, now=datetime_now(), charger_id=newly_added_charger.id)]
                    LOG.info('serial_id_list: %s' % serial_id_list)

                    if len(serial_id_list) == max_nozzle_guns_value:
                        raise ConflictParameterError(field_errors=[InvalidFieldError(
                            message=ErrorMessages.ReachedMaxLimit.value, field=FieldErrors.Nozzles)])

                    if nozzle_serial_id in [t.serial_id for t in nozzles_repository.fetch_all_serial_id_by_station_id(
                            station_id=station_id, now=datetime_now())]:
                        raise ConflictParameterError(field_errors=[InvalidFieldError(
                            message=ErrorMessages.SerialIDExists.value, field=FieldErrors.NozzlesSerialId)])

                    service_rates = service_rates_repository.fetch_by_service_master_record_id(
                        service_master_record_id=rated_power_id, now=datetime_now())

                    newly_added_nozzle = nozzles_repository.insert(charger_record_id=newly_added_charger.id,
                                                                   charging_connector_record_id=charging_connector_id,
                                                                   rated_power_record_id=rated_power_id,
                                                                   asset_id=asset_id, req_auth_claims=req_auth_claims,
                                                                   nozzle_serial_id=nozzle_serial_id)

                    station_services_repository.insert(station_record_id=station_id,
                                                       req_auth_claims=req_auth_claims,
                                                       service_master_record=rated_power_id,
                                                       custom_service_rate_record_id=service_rates.id)

                    nozzle_list.append({
                        "chargingConnector": {
                            "id": charging_connector_id
                        },
                        "ratedPower": {
                            "id": rated_power_id
                        },
                        "nozzleId": newly_added_nozzle.id,
                        "assetId": nozzle_asset_id,
                        "serialId": nozzle_serial_id,
                        "name": connector_name,
                        "rank": nozzle_rank
                    })

                added_chargers.append({
                    "chargerId": newly_added_equipment.id,
                    "type": equipment_type.value,
                    "serialId": serial_id,
                    "productId": product_id,
                    "modelId": model_id,
                    "assetId": asset_id,
                    "name": charger_name,
                    "rank": charger_rank,
                    "station": {
                        "id": station_id
                    },
                    "nozzles": nozzle_list
                })

        return {
            "chargers": added_chargers
        }

    def get_icon_image(self, icon_id, size=None):
        equipment_type_masters_repository = EquipmentTypeMasterRepository()
        image = equipment_type_masters_repository.fetch_icon_image_by_id(record_id=icon_id,
                                                                         now=datetime_now())

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

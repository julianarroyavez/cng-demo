from app.database import db_session
from app.domain.auth_schema import EquipmentTypes, MobileOS, MobileDevices
from app.errors import InvalidParameterError, MissingFieldError, FieldErrors
from app.log import LOG
from app.repository.equipments_repository import EquipmentsRepository
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.util.datetime_util import datetime_now


class DeviceService:
    def validate_device_registration_request(self, req_body):
        if "productId" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.productId)])

        if "modelId" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.modelId)])

        if "deviceToken" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.deviceToken)])

        if "os" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.osName)])

        if "osVersion" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.osVersion)])

        if "brand" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.brand)])

        if "appVersion" not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.appVersion)])

        if ("pushToken" not in req_body) or (req_body["pushToken"] is None) or (len(req_body["pushToken"]) == 0):
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.pushToken)])

    def device_registration(self, req_body, req_auth_claims):
        self.validate_device_registration_request(req_body)

        user = req_auth_claims.get('user')
        product_id = req_body['productId']
        model_id = req_body['modelId']
        device_token = req_body['deviceToken']
        os_name = MobileOS.from_str(req_body['os'])
        os_version = req_body['osVersion']
        brand = req_body['brand']
        app_version = req_body['appVersion']
        fcm_token = req_body['pushToken']

        mobile_devices_repository = MobileDevicesRepository()
        equipments_repository = EquipmentsRepository()

        now = datetime_now()
        with db_session.atomic():
            try:
                existing_device = mobile_devices_repository.fetch_by_device_token(device_token=device_token,
                                                                                  now=now)

                mobile_devices_repository.update_temporal_record(record=existing_device, user=user,
                                                                 record_id=existing_device.id,
                                                                 now=now)
                record_id = existing_device.record_id
                device_id = None

            except (MobileDevices.DoesNotExist, Exception):
                LOG.info("Device not exists...adding new device")

                newly_added_equipment = equipments_repository.insert(equipment_type=EquipmentTypes.MobileDevice,
                                                                     serial_id=None, product_id=product_id,
                                                                     model_id=model_id, asset_id=device_token,
                                                                     req_auth_claims=req_auth_claims)
                record_id = newly_added_equipment.id
                device_id = record_id

            mobile_devices_repository.insert(user=user, product_id=product_id, model_id=model_id,
                                             device_token=device_token, os_name=os_name, os_version=os_version,
                                             brand=brand, app_version=app_version, fcm_token=fcm_token,
                                             record_id=record_id, now=now, device_id=device_id)

        return {
            "userId": user,
            "productId": product_id,
            "modelId": model_id,
            "deviceToken": device_token,
            "os": os_name.value,
            "osVersion": os_version,
            "brand": brand,
            "appVersion": app_version,
            "pushToken": fcm_token
        }

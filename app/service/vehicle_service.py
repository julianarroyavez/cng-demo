import enum
import uuid

from app import log
from app.database import db_session
from app.domain.resource_schema import Vehicles, VehicleMasters, VerificationStatus
from app.errors import InvalidParameterError, MissingFieldError, FieldErrors, InvalidFieldError, ConflictParameterError, \
    ErrorMessages
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.repository.users_repository import UsersRepository
from app.repository.vehicle_masters_repository import VehicleMastersRepository
from app.repository.vehicles_repository import VehiclesRepository
from app.repository.verifications_repository import VerificationsRepository
from app.service.notification_service import NotificationService
from app.util import image_util, string_util
from app.util.datetime_util import datetime_now
from app.util.notification_factory import NotificationFactory

LOG = log.get_logger()


def validate_register_vehicle_request(req_body, req_file):
    if 'maker' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleMake)])

    if not string_util.check_if_alphanumeric(req_body['registrationNumber']):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.VehicleRegistrationNumber)])

    if 'model' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleModel)])

    # todo uncomment once finish uat server
    # if 'manufactureYear' not in req_body:
    #     raise InvalidParameterError('Year of Manufacturing is missing')

    if 'registrationNumber' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleRegistrationNumber)])

    if not req_file:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleRegistrationImage)])


def validate_verify_vehicle_request(req_body):
    if ('registeredVehicle' not in req_body) or ('id' not in req_body['registeredVehicle']):
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleId)])

    if 'verificationStatus' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VerificationStatus)])


class VehicleService:
    class Links(enum.Enum):
        RegistrationCertificateImage = '/api/v1/vehicles/{vehicle_id}/certificate-image'

        def href(self, vehicle_id):
            return self.value.format(**dict(vehicle_id=vehicle_id))

    def register_vehicle(self, req_body, req_file, req_auth_claims):
        """
        :param req_auth_claims:
        :param req_file:
        :param req_body: dict object of request body parsed from JsonParser() middleware
        """
        validate_register_vehicle_request(req_body, req_file)

        vehicle_masters_repository = VehicleMastersRepository()
        vehicle_repository = VehiclesRepository()
        notification_factory = NotificationFactory()
        notification_service = NotificationService()

        registration_number = req_body['registrationNumber']

        if vehicle_repository.validate_by_registration_number(registration_number):
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.RCNumberExists.value, field=FieldErrors.VehicleRegistrationNumber)])

        registration_certificate_image = req_file.read()

        vehicle_master = vehicle_masters_repository.fetch_by_record_id(record_id=req_body['vehicleMaster']['id'],
                                                                       now=datetime_now()).dicts().get()

        primary_key = str(uuid.uuid4())

        with db_session.atomic():
            newly_added_vehicle = vehicle_repository.insert(primary_key=primary_key,
                                                            user_id=req_auth_claims.get('user'),
                                                            registration_number=registration_number,
                                                            registration_certificate_image=registration_certificate_image,
                                                            vehicle_master_id=vehicle_master['record_id'])
            VerificationsRepository().insert(registered_by=req_auth_claims.get('user'), vehicle_id=primary_key)

            notification = notification_factory.create_and_queue_notification(data=newly_added_vehicle,
                                                                              user_id=req_auth_claims['user'],
                                                                              device_token=req_auth_claims[
                                                                                  'deviceToken'],
                                                                              device=None,
                                                                              trigger='Vehicle_added')

            notification_service.insert_notification(notifications=notification['notifications'],
                                                     to_device=notification['to_device'])

        return {
            "id": newly_added_vehicle.record_id,
            "maker": req_body["maker"],
            "model": req_body["model"],
            "manufacturingYear": req_body["manufacturingYear"],
            "registrationNumber": registration_number,
            "registrationCertificate": {
                "href": self.Links.RegistrationCertificateImage.href(vehicle_id=newly_added_vehicle.record_id)
            }
        }

    def register_cng_vehicle(self, req_body, req_auth_claims):
        """
        :param req_auth_claims:
        :param req_body: dict object of request body parsed from JsonParser() middleware
        """
        vehicle_masters_repository = VehicleMastersRepository()
        vehicle_master_list = vehicle_masters_repository.fetch_by_class_name("CNG_"+req_body["cngVehicleType"].upper(),
                                                                             now=datetime_now())

        vehicle_master_by_class = vehicle_master_list[0]
        vehicle_repository = VehiclesRepository()
        registration_number = req_body['vehicleRegistrationNumber']

        if vehicle_repository.validate_by_registration_number(registration_number):
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.RCNumberExists.value, field=FieldErrors.VehicleRegistrationNumber)])

        primary_key = str(uuid.uuid4())

        with db_session.atomic():
            newly_added_vehicle = vehicle_repository.insert(primary_key=primary_key,
                                                            user_id=req_auth_claims.get('user'),
                                                            registration_number=registration_number,
                                                            registration_certificate_image=None,
                                                            vehicle_master_id=vehicle_master_by_class.record_id)
            VerificationsRepository().insert(registered_by=req_auth_claims.get('user'), vehicle_id=primary_key)

        return {
            "id": newly_added_vehicle.record_id,
            "cngType": vehicle_master_by_class.class_of_vehicle,
            "registrationNumber": registration_number
        }

    def get_vehicle_certificate_image(self, vehicle_id, size=None):
        vehicles_repository = VehiclesRepository()
        image = vehicles_repository.fetch_rc_image_by_vehicles_id(vehicle_id=vehicle_id, now=datetime_now())

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

    def get_user_vehicles(self, user_id):
        vehicles_repository = VehiclesRepository()
        columns = [Vehicles.record_id, Vehicles.registration_number, Vehicles.verified, VehicleMasters.record_id,
                   VehicleMasters.brand, VehicleMasters.model, VehicleMasters.manufacturing_year,
                   VehicleMasters.charging_connector_records]

        vehicles = vehicles_repository.fetch_all_by_user(columns=columns, user_id=user_id, now=datetime_now())

        vehicles_own_by_user = []

        for vehicle in vehicles:
            connectors = []
            for connector in vehicle.vehicle_master.charging_connector_records:
                data = {
                    "id": connector
                }
                connectors.append(data)

            vehicles_own_by_user.append({
                'id': vehicle.record_id,
                'registrationNumber': vehicle.registration_number,
                'brand': vehicle.vehicle_master.brand,
                'model': vehicle.vehicle_master.model,
                'manufacturingYear': vehicle.vehicle_master.manufacturing_year,
                'makeYear': vehicle.vehicle_master.manufacturing_year,  # todo: correct this
                'vehicleMaster': {
                    'id': vehicle.vehicle_master.record_id
                    # todo: refer vehicle master res brand, model, manufacturingYear
                },
                'connectors': connectors,
                'verified': vehicle.verified  # todo: rc_image
            })

        return {
            'vehicles': vehicles_own_by_user
        }

    def embed_vehicles(self, root_body, user_id, params):
        vehicles = self.get_user_vehicles(user_id)

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['vehicles'] = vehicles.pop('vehicles')

    def verify_vehicle(self, req_body, req_auth_claims):
        validate_verify_vehicle_request(req_body)
        now = datetime_now()

        vehicles_repository = VehiclesRepository()
        verifications_repository = VerificationsRepository()
        mobile_devices_repository = MobileDevicesRepository()
        notification_factory = NotificationFactory()
        user_repository = UsersRepository()
        notification_service = NotificationService()

        vehicle_id = req_body['registeredVehicle']['id']
        verification_status = req_body['verificationStatus']
        verifier_id = req_auth_claims.get('user')

        verified = verification_status == VerificationStatus.Verified.value
        status = VerificationStatus.Verified if verified else VerificationStatus.Rejected

        columns = [Vehicles.record_id, Vehicles.registration_number, Vehicles.verified, VehicleMasters.record_id,
                   VehicleMasters.brand, VehicleMasters.model, VehicleMasters.manufacturing_year,
                   VehicleMasters.charging_connector_records]
        vehicles = vehicles_repository.fetch_by_id(record_id=vehicle_id, now=now, columns=columns)
        vehicle = vehicles_repository.fetch_by_record_id(record_id=vehicle_id, now=now)

        if vehicles.verified:
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.AlreadyVerifiedVehicle.value, field=FieldErrors.Verified)])

        with db_session.atomic():
            verifications_repository.update_vehicles_records(now=datetime_now(), verifier_id=verifier_id,
                                                             status=status,
                                                             verifier_remark=req_body['verifierRemark'],
                                                             vehicle_record_id=vehicle.record_id)

            vehicles_repository.update_verified_state(vehicle=vehicle, verified=verified)
            user = user_repository.fetch_by_record_id(record_id=vehicle.user_record, now=datetime_now())
            device = mobile_devices_repository.fetch_by_user_phone_number(phone_number=user.phone_number)
            vehicle.verified = verified

        notification = notification_factory.create_and_queue_notification(data=vehicle, user_id=vehicle.user_record,
                                                                          device_token=None, device=device,
                                                                          trigger='Vehicle_verified')
        notification_service.insert_notification(notifications=notification['notifications'],
                                                 to_device=notification['to_device'])

        connectors = []
        for connector in vehicles.vehicle_master.charging_connector_records:
            data = {
                "id": connector
            }
            connectors.append(data)

        response = {"registeredVehicle": {
            "id": vehicles.record_id,
            "registrationNumber": vehicles.registration_number,
            "registrationCertificateImage": {
                "href": self.Links.RegistrationCertificateImage.href(vehicle_id=vehicle.record_id)
            },
            "brand": vehicles.vehicle_master.brand,
            "model": vehicles.vehicle_master.model,
            "manufacturingYear": vehicles.vehicle_master.manufacturing_year,
            "makeYear": vehicles.vehicle_master.manufacturing_year,
            "vehicleMaster": {
                "id": vehicles.vehicle_master.record_id
            },
            # "connector": {
            #     "id": vehicles.vehicle_master.charging_connector_record
            # },
            "verified": verified
        }, "verificationStatus": status.value, "verifierRemark": req_body['verifierRemark'], "verificationTime": now,
            "verifier": {
                "id": verifier_id
            }, 'connectors': connectors}
        return response

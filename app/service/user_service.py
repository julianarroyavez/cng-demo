import enum
import uuid
from app.database import db_session
from app.domain.auth_schema import Users, UserRoles, Roles
from app.domain.resource_schema import VerificationStatus
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.repository.user_group_rel_repository import UserGroupRelRepository
from app.repository.users_repository import UsersRepository
from app.repository.verifications_repository import VerificationsRepository
from app.service.notification_service import NotificationService
from app.service.vehicle_service import VehicleService
from app.util import image_util, string_util

from app.errors import InvalidParameterError, FileNotExistsError, MissingFieldError, FieldErrors, \
    ConflictParameterError, InvalidFieldError, ErrorMessages

# todo: can be manage using hooks
from app.util.Enums.gnc_vehicle_types import GncVehicleType
from app.util.datetime_util import datetime_now
from app.util.notification_factory import NotificationFactory


def validate_user_registration_request(req_body):
    if 'name' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.Name)])

    name = req_body['name'].replace(' ', '')
    if not string_util.check_if_alphanumeric(name):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Name)])

    if 'phoneNumber' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.PhoneNumber)])

    elif not string_util.check_if_alphanumeric(req_body['phoneNumber']):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

    if 'pincode' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.FPinCode)])

    elif not string_util.check_if_alphanumeric(req_body['pincode']):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PinCode)])

    if 'cngVehicleType' in req_body:
        if req_body["cngVehicleType"].title() not in GncVehicleType:
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.CngVehicleType)])
        if 'vehicleRegistrationNumber' not in req_body and not string_util.check_if_alphanumeric(
                req_body['vehicleRegistrationNumber']):
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VehicleRegistrationNumber)])

    if "mCardNumber" in req_body and not string_util.check_if_alphanumeric(req_body['mCardNumber']):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.MileageCardNumber)])

    if 'dlNumber' not in req_body and 'cngVehicleType' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.DrivingLicenceNumber)])

    if 'dlNumber' in req_body and not string_util.check_if_alphanumeric(req_body['dlNumber']):
        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.DrivingLicenceNumber)])


def validate_user_verify_request(req_body):
    if ('registeredUser' not in req_body) or ('id' not in req_body['registeredUser']):
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.UserId)])

    if 'verificationStatus' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VerificationStatus)])


class UserService:
    class Links(enum.Enum):
        DrivingLicenceImage = '/api/v1/users/{key}/driving-licence-image'
        ProfileImage = '/api/v1/users/{key}/profile-image'

        def href(self, key):
            return self.value.format(**dict(key=key))

    def evo_user_registration(self, req_body, req_file, req_auth_claims):
        user_repository = UsersRepository()
        validate_user_registration_request(req_body)

        if user_repository.validate_by_dl_number(dl_number=req_body['dlNumber']):
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.DLNumberExists.value, field=FieldErrors.DrivingLicenceNumber)])

        if user_repository.validate_by_phone_number(phone_number=req_body['phoneNumber'], now=datetime_now(),
                                                    role=UserRoles.Guest):
            raise ConflictParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.EVOwnerExists.value,
                                                                         field=FieldErrors.PhoneNumber)])

        with db_session.atomic():
            primary_key = str(uuid.uuid4())
            user = user_repository.update_temporal_record(
                primary_key=primary_key,
                record_id=req_auth_claims.get('user'),
                phone_number=req_body['phoneNumber'],
                name=req_body['name'],
                email=req_body['email'],
                pin_code=req_body['pincode'],
                licence_number=req_body['dlNumber'],
                licence_number_image=req_file,
                now=datetime_now(),
                mileage_card_number=req_body['mCardNumber'] if 'mCardNumber' in req_body else '')

            UserGroupRelRepository().update_to_ev_owner(user=user, now=datetime_now())
            VerificationsRepository().insert(registered_by=primary_key, user_id=req_auth_claims.get('user'))

        return {
            "id": user.record_id,
            "name": user.name,
            "phoneNumber": user.phone_number,
            "options": {
                "countryCode": "+91"
            },
            "email": user.email,
            "pincode": user.pin_code,
            "dlNumber": user.licence_number,
            "dlImage": {
                "href": self.Links.DrivingLicenceImage.href(key=user.record_id)
            },
            "profileImage": {
                "href": self.Links.ProfileImage.href(key=user.record_id)
            },
            "_links": {
                "self": {
                    "href": "url to access self authn entry"
                }
            },
            "createdTime": user.created_on.isoformat()
        }

    def cng_vo_user_registration(self, req_body, req_file, req_auth_claims):
        user_repository = UsersRepository()
        validate_user_registration_request(req_body)

        if user_repository.validate_by_phone_number(phone_number=req_body['phoneNumber'], now=datetime_now(),
                                                    role=UserRoles.Guest):
            raise ConflictParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.EVOwnerExists.value,
                                                                         field=FieldErrors.PhoneNumber)])

        with db_session.atomic():
            primary_key = str(uuid.uuid4())
            user = user_repository.update_temporal_record(
                primary_key=primary_key,
                record_id=req_auth_claims.get('user'),
                phone_number=req_body['phoneNumber'],
                name=req_body['name'],
                email=req_body['email'] if 'email' in req_body else None,
                pin_code=req_body['pincode'],
                licence_number=req_body['dlNumber'] if 'dlNumber' in req_body else None,
                licence_number_image=req_file,
                now=datetime_now(),
                mileage_card_number=req_body['mCardNumber'] if 'mCardNumber' in req_body else None)

            UserGroupRelRepository().update_to_ev_owner(user=user, now=datetime_now())
            VerificationsRepository().insert(registered_by=primary_key, user_id=req_auth_claims.get('user'))
            vehicle_service = VehicleService()

            vehicle_response = vehicle_service.register_cng_vehicle(req_body, req_auth_claims=req_auth_claims)

        return {
            "id": user.record_id,
            "name": user.name,
            "phoneNumber": user.phone_number,
            "options": {
                "countryCode": "+91"
            },
            "email": user.email,
            "pincode": user.pin_code,
            "dlNumber": user.licence_number,
            "createdTime": user.created_on.isoformat(),
            "vehicle": vehicle_response
        }

    def get_users_dl_image(self, user_id, size=None):
        users_repository = UsersRepository()
        image = users_repository.fetch_dl_image_by_record_id(user_id=user_id, now=datetime_now())

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

    def get_users_profile_image(self, user_id, size=None):
        users_repository = UsersRepository()
        image = users_repository.fetch_profile_image_by_record_id(user_id=user_id, now=datetime_now())
        if image is None:
            raise FileNotExistsError(description="data not found")

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

    def get_user_profile(self, req_auth_claims):
        user_repository = UsersRepository()
        user = user_repository.fetch_by_record_id(record_id=req_auth_claims.get('user'), now=datetime_now())

        profile = {
            "id": str(user.record_id),
            "customerId": str(user.customer_id),
            "phoneNumber": user.phone_number,
            "name": user.name,
            "licenceNumber": user.licence_number,
            "profileImage": {
                "href": self.Links.ProfileImage.href(key=user.record_id)
            },
            "verified": user.verified
        }

        return profile

    def embed_user(self, root_body, user_id, params):
        user_repository = UsersRepository()

        columns = [Users.record_id, Users.customer_id, Users.phone_number, Users.name, Users.licence_number,
                   Users.verified, Roles.name]
        user = user_repository.fetch_all_details_with_role_by_record_id(columns=columns, record_id=user_id,
                                                                        now=datetime_now())

        user_to_embed = {
            'id': user.record_id,
            'customerId': user.customer_id,
            'phoneNumber': user.phone_number,
            'name': user.name,
            'userRole': user.user_group_rel.roles.name.value,
            'licenceNumber': user.licence_number,
            "profileImage": {
                "href": self.Links.ProfileImage.href(key=user.record_id)
            },
            'verified': user.verified
        }

        if root_body.get('_embedded', None) is None:
            root_body['_embedded'] = {
                'user': user_to_embed
            }
        else:
            root_body['_embedded']['user'] = user_to_embed
        return root_body

    def get_evo_details(self, role_type, phone_number):

        users_list = []
        try:
            role = UserRoles.from_str(string=role_type)
        except Exception:
            UserRoles.from_str(string=role_type)

        users_repository = UsersRepository()
        if phone_number is not None:
            users = users_repository.fetch_all_by_phone_number_and_role(phone_number=phone_number, now=datetime_now(),
                                                                        role=role)
            if not users:
                raise ConflictParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.InvalidEVOwner.value,
                                                                             field=FieldErrors.PhoneNumber)])

        else:
            users = users_repository.fetch_all_by_validity(now=datetime_now())

        for user in users:
            users_list.append({
                "id": user.record_id,
                "customerId": user.record_id,
                "phoneNumber": user.phone_number,
                "name": user.name,
                "licenceNumber": user.licence_number,
                "licenceImage": {
                    "href": self.Links.DrivingLicenceImage.href(key=user.record_id)
                },
                "verified": user.verified
            })
        return {
            "users": users_list
        }

    def verify_user(self, req_body, req_auth_claims):
        validate_user_verify_request(req_body)
        now = datetime_now()
        mobile_devices_repository = MobileDevicesRepository()
        notification_factory = NotificationFactory()
        notification_service = NotificationService()

        users_repository = UsersRepository()
        verifications_repository = VerificationsRepository()

        user_id = req_body['registeredUser']['id']
        verification_status = req_body['verificationStatus']
        verifier_id = req_auth_claims.get('user')

        verified = verification_status == VerificationStatus.Verified.value
        status = VerificationStatus.Verified if verified else VerificationStatus.Rejected

        user = users_repository.fetch_by_record_id(record_id=user_id, now=now)

        if user.verified:
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.AlreadyVerifiedEVOwner.value, field=FieldErrors.Verified)])

        with db_session.atomic():
            verifications_repository.update_users_records(user_record_id=user.record_id, verifier_id=verifier_id,
                                                          now=now, verifier_remark=req_body['verifierRemark'],
                                                          status=status)
            users_repository.update_verified_state(user=user, verified=verified)

            user = users_repository.fetch_by_record_id(record_id=user.record_id, now=datetime_now())
            device = mobile_devices_repository.fetch_by_user_phone_number(phone_number=user.phone_number)
            user.verified = verified
            notification = notification_factory.create_and_queue_notification(data=user, user_id=user_id, device=device,
                                                                              device_token=None,
                                                                              trigger='User_verified')
            notification_service.insert_notification(notifications=notification['notifications'],
                                                     to_device=notification['to_device'])

        return {
            "registeredUser": {
                "id": user.record_id,
                "customerId": user.record_id,
                "phoneNumber": user.phone_number,
                "name": user.name,
                "licenceNumber": user.licence_number,
                "licenceImage": {
                    "href": self.Links.DrivingLicenceImage.href(key=user.record_id)
                },
                "verified": verified
            },
            "verificationStatus": status.value,
            "verifierRemark": req_body['verifierRemark'],
            "verificationTime": now,
            "verifier": {
                "id": verifier_id
            }
        }

    def validate_station_owner_registration_request(self, req_body, req_auth_claims):
        self.validate_user(user_id=req_auth_claims.get('user'))
        if 'phoneNumber' not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.PhoneNumber)])

        elif not string_util.check_if_alphanumeric(req_body['phoneNumber']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

    def validate_user(self, user_id):
        user_group_rel_repository = UserGroupRelRepository()
        user = user_group_rel_repository.fetch_by_user_id(user_id=user_id, now=datetime_now())

        if user.group_id != 1:
            raise ConflictParameterError(field_errors=[InvalidFieldError(
                message=ErrorMessages.AlreadyRegisteredEVSO.value, field=FieldErrors.PhoneNumber)])

    def evso_user_registration(self, req_body, req_auth_claims):
        user_repository = UsersRepository()
        self.validate_station_owner_registration_request(req_body=req_body, req_auth_claims=req_auth_claims)

        if user_repository.validate_by_phone_number(phone_number=req_body['phoneNumber'], now=datetime_now(),
                                                    role=UserRoles.Guest):
            raise ConflictParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.InvalidNumber.value,
                                                                         field=FieldErrors.PhoneNumber)])

        with db_session.atomic():
            primary_key = str(uuid.uuid4())
            user = user_repository.update_evso_temporal_record(
                primary_key=primary_key,
                record_id=req_auth_claims.get('user'),
                phone_number=req_body['phoneNumber'],
                now=datetime_now())

            UserGroupRelRepository().update_to_evs_owner(user=req_auth_claims, now=datetime_now())

        return {
            "id": user.record_id,
            "phoneNumber": user.phone_number,
            "options": {
                "countryCode": "+91"
            },
            "createdTime": user.created_on.isoformat()
        }

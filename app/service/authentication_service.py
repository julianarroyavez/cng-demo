import enum
import uuid

from jwt import ExpiredSignatureError

from app import config
from app.domain.auth_schema import AuthenticationState, Users
from app.errors import InvalidParameterError, InvalidStateError, MissingFieldError, FieldErrors
from app.log import LOG
from app.repository.auth_attempts_repository import AuthAttemptsRepository
from app.repository.users_repository import UsersRepository
from app.service import token_service
from app.service.notification_service import NotificationService
from app.service.sms_service import SmsService
from app.util import string_util
from app.util.datetime_util import datetime_now, before_now
from app.util.encryption.encryption_util import EncryptionUtil
from app.util.notification_factory import NotificationFactory

AuthenticationStateDesc = {
    AuthenticationState.Unauthorized: "step-up attempt",
    AuthenticationState.OtpRequired: "waiting to verify OTP",
    AuthenticationState.OtpFailed: "fails to verify OTP before reaching to max verification attempts",
    AuthenticationState.OtpRestricted: "reached max verification attempts",
    AuthenticationState.Restricted: "reached max authentication attempts",
    AuthenticationState.Discarded: "tried new authentication attempt discarding this",
    AuthenticationState.RefreshFailed: "failed to refresh token as refresh token is invalid or expired",
    AuthenticationState.Success: "successful authentication attempt",
    AuthenticationState.OtpSendFailed: "failed to send OTP before reaching max send attempts"
}

MaxOtpVerificationAttempts = int(config.OTP['max_otp_verification_attempts'])
MaxResendOtpAttempts = int(config.OTP['max_resend_otp_attempts'])
MaxResendOtpAttemptWindowInMin = int(config.OTP['max_resend_otp_attempt_window_in_min'])
OtpValidityInSecs = int(config.OTP['otp_validity_in_secs'])  # todo use this in logic


def validate_verify_otp_request(req_body, txn_id):
    if 'otp' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.Otp)])

    if 'stateToken' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.StateToken)])

    if not txn_id:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.StateToken)])


def validate_request_otp_request(req_body):
    if 'verificationFactor' not in req_body:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.VerificationFactor)])

    if 'phoneNumber' not in req_body or len(req_body['phoneNumber']) != 10:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.PhoneNumber)])

    if 'options' not in req_body or 'countryCode' not in req_body['options']:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.CountryCode)])

    if 'context' not in req_body or 'deviceToken' not in req_body['context']:
        raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.DeviceToken)])


class AuthenticationService:
    class Links(enum.Enum):
        Self = '/api/v1/authn/{txn_id}'
        Next = '/api/v1/authn/{txn_id}/verify'

        def href(self, txn_id):
            return self.value.format(**dict(txn_id=txn_id))

    def request_otp(self, req_body):
        """
        :param req_body: dict object of request body parsed from JsonParser() middleware
        """
        validate_request_otp_request(req_body)
        device_token = req_body['context']['deviceToken']
        phone_number = req_body['phoneNumber']
        user_key = req_body['context']['userKey']

        encryption_util = EncryptionUtil()
        sha_hash = encryption_util.gen_sha_256_hash(key=device_token)
        LOG.info(sha_hash)
        is_valid_hash = encryption_util.is_valid_hash(source_hash=user_key, destination_hash=sha_hash)

        if not is_valid_hash:
            return {
                "createdTime": datetime_now(),
                "status": AuthenticationState.OtpSendFailed.value,
                "statusDesc": AuthenticationStateDesc[AuthenticationState.OtpSendFailed],
                "stateToken": uuid.uuid4(),
                "attemptsRemaining": 0,
                "_links": {
                    "self": {
                        "href": '/api/v1/authn'
                    }
                }
            }

        auth_attempts_repository = AuthAttemptsRepository()
        attempts = auth_attempts_repository.fetch_all_previous_records_for_user(phone_number=phone_number,
                                                                                device_token=device_token,
                                                                                records_after_time=before_now(
                                                                                    minutes=
                                                                                    MaxResendOtpAttemptWindowInMin
                                                                                ))

        if len(attempts) >= MaxResendOtpAttempts:
            # update last attempt
            auth_attempt = attempts[0]

            auth_attempt.state = AuthenticationState.Restricted
            auth_attempt.state_desc = AuthenticationStateDesc[auth_attempt.state]
            auth_attempts_repository.update(record=auth_attempt, modified_on=datetime_now())

            return {
                "stateToken": auth_attempt.txn_id,
                "attemptsRemaining": MaxOtpVerificationAttempts - auth_attempt.verification_attempt_count,
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                    }
                },
                "createdTime": auth_attempt.modified_on,
                "status": auth_attempt.state.value,
                "statusDesc": auth_attempt.state_desc
            }

        if 'stateToken' in req_body:
            # update older attempt to discarded
            auth_attempt = auth_attempts_repository.fetch_by_txn_id(txn_id=req_body['stateToken'])

            auth_attempt.state = AuthenticationState.Discarded
            auth_attempt.state_desc = AuthenticationStateDesc[auth_attempt.state]
            auth_attempts_repository.update(record=auth_attempt, modified_on=datetime_now())

        otp = int(string_util.generate_otp()) if phone_number != config.SMS['default_number'] else 123456
        # todo get length of otp from app_configs
        txn_id = str(uuid.uuid4())

        user_repository = UsersRepository()
        audit_user = user_repository.fetch_prospect_user(now=datetime_now())

        new_attempt = auth_attempts_repository.insert(txn_id=txn_id,
                                                      device_token=req_body['context']['deviceToken'],
                                                      country_code=req_body['options']['countryCode'],
                                                      phone_number=req_body['phoneNumber'],
                                                      backing_txn_id=req_body.get('stateToken', None),
                                                      otp=otp,
                                                      state=AuthenticationState.OtpRequired,
                                                      state_desc=AuthenticationStateDesc[
                                                          AuthenticationState.OtpRequired],
                                                      audit_user=audit_user)

        SmsService().send_otp_sms(req_body['phoneNumber'], otp, txn_id=new_attempt.txn_id)
        return {
            "stateToken": new_attempt.txn_id,
            "status": new_attempt.state.value,
            "statusDesc": new_attempt.state_desc,
            "attemptsRemaining": MaxOtpVerificationAttempts - new_attempt.verification_attempt_count,
            "_links": {
                "self": {
                    "href": self.Links.Self.href(txn_id=txn_id)
                },
                "next": {
                    "href": self.Links.Next.href(txn_id=txn_id)
                }
            }
        }

    def verify_otp(self, req_body, txn_id):
        validate_verify_otp_request(req_body, txn_id)

        auth_attempts_repository = AuthAttemptsRepository()
        notification_factory = NotificationFactory()
        auth_attempt = auth_attempts_repository.fetch_by_txn_id(txn_id=txn_id)
        notification_service = NotificationService()

        if auth_attempt.state not in [AuthenticationState.OtpRequired, AuthenticationState.OtpFailed]:
            raise InvalidStateError(description='attempt state not as per required')

        if auth_attempt.verification_attempt_count >= MaxOtpVerificationAttempts:
            auth_attempt.state = AuthenticationState.OtpRestricted
            auth_attempt.state_desc = AuthenticationStateDesc[auth_attempt.state]
            auth_attempts_repository.update(record=auth_attempt, modified_on=datetime_now())

            return {
                "stateToken": req_body['stateToken'],
                "attemptsRemaining": MaxOtpVerificationAttempts - auth_attempt.verification_attempt_count,
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                    }
                },
                "createdTime": auth_attempt.modified_on,
                "status": auth_attempt.state.value,
                "statusDesc": auth_attempt.state_desc
            }

        if req_body['otp'] != auth_attempt.otp:
            auth_attempt.state = AuthenticationState.OtpFailed
            auth_attempt.state_desc = AuthenticationStateDesc[auth_attempt.state]
            auth_attempt.verification_attempt_count = 1 + auth_attempt.verification_attempt_count
            auth_attempts_repository.update(record=auth_attempt, modified_on=datetime_now())

            return {
                "stateToken": req_body['stateToken'],
                "attemptsRemaining": MaxOtpVerificationAttempts - auth_attempt.verification_attempt_count,
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                    }
                },
                "createdTime": auth_attempt.modified_on,
                "status": auth_attempt.state.value,
                "statusDesc": auth_attempt.state_desc
            }

        users_repository = UsersRepository()
        try:
            session_user = users_repository.fetch_by_phone_number(phone_number=auth_attempt.phone_number,
                                                                  now=datetime_now())

        except (Users.DoesNotExist, Exception):
            LOG.info('user doesn\'t exist creating new user %s ' % auth_attempt.phone_number)
            session_user = users_repository.insert(phone_number=auth_attempt.phone_number)

        session_token = token_service.issue_new_token(valid_auth_attempt=auth_attempt, session_user=session_user)
        refresh_token = token_service.issue_refresh_token(auth_attempt)

        LOG.debug('jwt token: %s' % session_token)
        LOG.debug('refresh token: %s' % refresh_token)

        auth_attempt.state = AuthenticationState.Success
        auth_attempt.state_desc = AuthenticationStateDesc[auth_attempt.state]
        auth_attempt.verification_attempt_count = 1 + auth_attempt.verification_attempt_count
        auth_attempts_repository.update(record=auth_attempt, modified_on=datetime_now())

        optional_data = {
            "fcm_token": req_body['context']['fcmToken']
        }
        notification = notification_factory.create_and_queue_notification(data=auth_attempt, device_token=None,
                                                                          user_id=session_user.record_id,
                                                                          device=None, trigger='Login',
                                                                          optional_data=optional_data)

        notification_service.insert_notification(notifications=notification['notifications'],
                                                 to_device=notification['to_device'])

        return {
            "stateToken": req_body['stateToken'],
            "attemptsRemaining": MaxOtpVerificationAttempts - auth_attempt.verification_attempt_count,
            "_links": {
                "self": {
                    "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                }
            },
            "createdTime": auth_attempt.modified_on,
            "status": auth_attempt.state.value,
            "statusDesc": auth_attempt.state_desc,
            "sessionToken": session_token,
            "refreshToken": refresh_token
        }

    def handle_refresh_token_request(self, req_body):
        auth_attempts_repository = AuthAttemptsRepository()
        users_repository = UsersRepository()

        refresh_token = req_body.get('refreshToken')
        claims = token_service.decode_token(refresh_token, verify_expiry=False)

        try:
            token_service.validate_token_claims(claims)
        except ExpiredSignatureError:
            auth_attempt = auth_attempts_repository.insert(txn_id=str(uuid.uuid4()),
                                                           device_token=claims.get('deviceToken'),
                                                           country_code=None,
                                                           phone_number=claims.get('phoneNumber'),
                                                           otp=None,
                                                           state=AuthenticationState.RefreshFailed,
                                                           state_desc=AuthenticationStateDesc[
                                                               AuthenticationState.RefreshFailed],
                                                           backing_txn_id=claims.get('jti'),
                                                           audit_user=claims.get('user'))

            return {
                "_links": {
                    "self": {
                        "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                    }
                },
                "createdTime": auth_attempt.modified_on,
                "status": auth_attempt.state.value,
                "statusDesc": auth_attempt.state_desc
            }

        auth_attempt = auth_attempts_repository.insert(txn_id=str(uuid.uuid4()),
                                                       device_token=claims.get('deviceToken'),
                                                       country_code=None,
                                                       phone_number=claims.get('phoneNumber'),
                                                       otp=None,
                                                       state=AuthenticationState.Success,
                                                       state_desc=AuthenticationStateDesc[AuthenticationState.Success],
                                                       backing_txn_id=claims.get('jti'),
                                                       audit_user=claims.get('user'))

        try:
            session_user = users_repository.fetch_by_phone_number(phone_number=auth_attempt.phone_number,
                                                                  now=datetime_now())
        except (Users.DoesNotExist, Exception):
            LOG.info('user doesn\'t exist creating new user %s ' % auth_attempt.phone_number)
            session_user = users_repository.insert(phone_number=auth_attempt.phone_number)

        session_token = token_service.issue_new_token(valid_auth_attempt=auth_attempt, session_user=session_user)
        refresh_token = token_service.issue_refresh_token(auth_attempt)

        return {
            "_links": {
                "self": {
                    "href": self.Links.Self.href(txn_id=auth_attempt.txn_id)
                }
            },
            "createdTime": auth_attempt.modified_on,
            "status": auth_attempt.state.value,
            "statusDesc": auth_attempt.state_desc,
            "sessionToken": session_token,
            "refreshToken": refresh_token
        }

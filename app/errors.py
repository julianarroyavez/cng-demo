# -*- coding: utf-8 -*-
import enum

import falcon

from app.log import LOG
from app.util.json_util import to_json

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict


class FieldErrors(enum.Enum):
    MultipartFile = 101
    VerificationFactor = 102
    StateToken = 103
    Otp = 104
    PhoneNumber = 105
    CountryCode = 106
    DeviceToken = 107
    Name = 108
    PinCode = 109
    DrivingLicenceNumber = 110
    VehicleMake = 111
    VehicleModel = 112
    VehicleRegistrationNumber = 113
    VehicleRegistrationImage = 114
    StationRegistrationHyggeBox = 115
    StationRegistrationOperationDetails = 116
    StationRegistrationImage = 117
    Verified = 118
    VehicleId = 119
    UserId = 120
    VerificationStatus = 121
    RoleType = 141
    Nozzles = 122
    ChargerType = 123
    ChargersSerialId = 124
    ChargersRank = 125
    StationId = 126
    ChargingConnectorId = 127
    RatedPowerId = 128
    ChargersName = 129  # todo with dependency
    NozzlesSerialId = 130
    NozzlesName = 131  # todo with dependency
    NozzlesRank = 132
    Balance = 133
    Notification = 134
    Email = 135
    Token = 136
    Rating = 137
    Query = 138
    CngVehicleType = 139
    MileageCardNumber = 140


class AppError(falcon.HTTPError):
    __slots__ = (
        'message',
        'raw_exception',
    )

    def __init__(self, status=falcon.HTTP_500, message="Something went wrong. Please try again later",
                 raw_exception=None, **kwargs):
        super(AppError, self).__init__(status, **kwargs)
        self.message = message
        self.raw_exception = raw_exception

    @classmethod
    def from_falcon_error(cls, falcon_error):
        return cls(message=falcon_error.title,
                   title=falcon_error.title,
                   code=falcon_error.code,
                   description=falcon_error.description,
                   status=falcon_error.status)

    def to_dict(self, obj_type=dict):
        error_body = obj_type()
        error_body["errorCode"] = self.code
        error_body["errorTitle"] = self.title
        error_body["errorMessage"] = self.message
        error_body["errorDescription"] = self.description
        return error_body

    @staticmethod
    def handle(exception, req, res, error=None):
        if exception.raw_exception is not None:
            LOG.error("caused by: {}".format(exception.raw_exception))
        res.status = exception.status
        res.body = to_json(exception.to_dict())

    @staticmethod
    def handle_raw(exception, req, res, error=None):
        if exception is not None:
            LOG.error("caused by: {}".format(exception))
        app_exception = UnknownError(raw_exception=exception)
        res.status = app_exception.status
        res.body = to_json(app_exception.to_dict())


class InvalidParameterError(AppError):
    def __init__(self, code=None, message=None, description=None, field_errors=None, **kwargs):
        super().__init__(
            status=falcon.HTTP_400,
            code=code or 80,
            title="Validation Failure",
            message=message or "Invalid data",
            description=description,
            **kwargs
        )
        self.field_errors = field_errors

    def to_dict(self, obj_type=dict):
        error_body = super(InvalidParameterError, self).to_dict()
        error_body["fieldErrors"] = [field_error.to_dict() for field_error in
                                     self.field_errors] if self.field_errors else None
        return error_body


class ConflictParameterError(InvalidParameterError):
    def __init__(self, field=None, message=None, description=None, field_errors=None, **kwargs):
        super().__init__(
            code=81,
            message=message or "Existing data",
            description=description,
            field_errors=field_errors,
            **kwargs
        )


class InvalidFieldError(AppError):
    def __init__(self, field=None, message=None, description=None):
        super().__init__(
            status=falcon.HTTP_400,
            code=field.value or 100,
            title="Invalid field",
            message=message or "{} is invalid".format(field.name),
            description=description
        )
        self.field = field.name

    def to_dict(self, obj_type=dict):
        error_body = super(InvalidFieldError, self).to_dict()
        error_body["field"] = self.field
        return error_body


class MissingFieldError(InvalidFieldError):
    def __init__(self, field=None, message=None, description=None):
        super(MissingFieldError, self).__init__(
            field=field,
            message=message or "{} is missing".format(field.name),
            description=description
        )


class InvalidStateError(AppError):
    def __init__(self, **kwargs):
        super(InvalidStateError, self).__init__(status=falcon.HTTP_400, code=70, title="Invalid State", **kwargs)


class DatabaseError(AppError):
    def __init__(self, **kwargs):
        super(DatabaseError, self).__init__(status=falcon.HTTP_400, code=91, title="Database Related Issue", **kwargs)


class UserNotExistsError(AppError):
    def __init__(self, **kwargs):
        super(UserNotExistsError, self).__init__(status=falcon.HTTP_400, code=83, title="Invalid User", **kwargs)


class UnauthorizedError(AppError):
    def __init__(self, **kwargs):
        super(UnauthorizedError, self).__init__(status=falcon.HTTP_UNAUTHORIZED, code=85,
                                                title="Authentication Required", **kwargs)


class ForbiddenError(AppError):
    def __init__(self, **kwargs):
        super(ForbiddenError, self).__init__(status=falcon.HTTP_FORBIDDEN, code=87, title="Authentication Forbidden",
                                             **kwargs)


class BalanceError(AppError):
    def __init__(self, **kwargs):
        super(BalanceError, self).__init__(status=falcon.HTTP_BAD_REQUEST, code=82, title="Insufficient Balance Error",
                                           **kwargs)


class FileNotExistsError(AppError):
    def __init__(self, **kwargs):
        super(FileNotExistsError, self).__init__(status=falcon.HTTP_NOT_FOUND, code=84, title="File does not exist",
                                                 **kwargs)


class UnknownError(AppError):
    def __init__(self, **kwargs):
        super(UnknownError, self).__init__(status=falcon.HTTP_INTERNAL_SERVER_ERROR, code=90, title="Unknown Error",
                                           **kwargs)


class ErrorMessages(enum.Enum):
    DLNumberExists = "Driving Licence number already exists."
    EVOwnerExists = "Ev owner already registered."
    RCNumberExists = "Registration certificate number already exists."
    SlotUnavailable = "This slot is not available."
    InvalidEVOwner = "This is not a valid EV Owner."
    AlreadyVerifiedEVOwner = "This EV Owner is already verified."
    AlreadyVerifiedVehicle = "This Vehicle is already verified"
    AlreadyRegisteredEVSO = "This EV station owner already registered."
    NotRegisteredUser = "This user is not registered."
    NotVerifiedUser = "This user is not verified."
    InvalidNumber = "This number is invalid."
    InsufficientBalance = "You Don't have sufficient balance."
    SerialIDExists = "This connector Serial id already exists."
    MaxConnector = "You can only add up to {max_nozzle_guns_value} connectors only."
    ReachedMaxLimit = "Reached maximum limit of connectors for this charger."
    InvalidUserForTokenTransfer = "This is not a valid EV Owner."

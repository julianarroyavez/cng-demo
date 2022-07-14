import enum

from peewee import UUIDField, CharField, BlobField, BooleanField, ForeignKeyField, BigAutoField, DeferredThroughModel, \
    ManyToManyField, CompositeKey, IntegerField
from playhouse.postgres_ext import BinaryJSONField

from app.constant import schema_constant
from app.domain.base import TemporalBaseModel, BaseModel, RawBaseModel, EnumField
from app.errors import InvalidParameterError, FieldErrors, InvalidFieldError


class EquipmentTypes(enum.Enum):
    MobileDevice = 'MOBILE_DEVICE'
    EvCharger = 'EV_CHARGER'
    Battery = 'BATTERY'
    BatteryCharger = 'BATTERY_CHARGER'

    @staticmethod
    def from_str(string):
        if string in ['EV_CHARGER']:
            return EquipmentTypes.EvCharger
        if string in ['MOBILE_DEVICE']:
            return EquipmentTypes.MobileDevice
        if string in ['BATTERY']:
            return EquipmentTypes.Battery
        if string in ['BATTERY_CHARGER']:
            return EquipmentTypes.BatteryCharger
        else:
            raise InvalidParameterError(description='Invalid Equipment Type',
                                        field_errors=[InvalidFieldError(FieldErrors.ChargerType)])


class EquipmentStatus(enum.Enum):
    Active = 'ACTIVE'
    UnderMaintenance = 'UNDER_MAINTENANCE'
    NonFunctional = 'NON_FUNCTIONAL'


class UserRoles(enum.Enum):
    Guest = 'GUEST'
    EvOwner = 'EV_OWNER'
    StationOwner = 'STATION_OWNER'
    StationAttendant = 'STATION_ATTENDANT'
    FieldOfficer = 'FIELD_OFFICER'
    SystemAdmin = 'SYSTEM_ADMIN'
    ServerAdmin = 'SERVER_ADMIN'

    @staticmethod
    def from_str(string):
        if string in ['GUEST']:
            return UserRoles.Guest
        if string in ['EV_OWNER']:
            return UserRoles.EvOwner
        if string in ['STATION_OWNER']:
            return UserRoles.StationOwner
        if string in ['STATION_ATTENDANT']:
            return UserRoles.StationAttendant
        if string in ['FIELD_OFFICER']:
            return UserRoles.FieldOfficer
        if string in ['SYSTEM_ADMIN']:
            return UserRoles.SystemAdmin
        if string in ['SERVER_ADMIN']:
            return UserRoles.ServerAdmin
        else:
            raise InvalidParameterError(description='Invalid RoleType',
                                        field_errors=[InvalidFieldError(FieldErrors.RoleType)])


class AccountType(enum.Enum):
    User = 'USER'
    Station = 'STATION'
    Admin = 'ADMIN'


class Accounts(TemporalBaseModel):
    id = UUIDField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    alias_name = CharField(max_length=50)
    type = EnumField(enum_class=AccountType)

    class Meta:
        schema = schema_constant.transactional


class Users(Accounts):
    customer_id = CharField(max_length=50)  # same as record_id
    phone_number = CharField(null=True, max_length=12)
    name = CharField(null=True, max_length=50)
    email = CharField(null=True, max_length=50)
    pin_code = CharField(null=True, max_length=10)
    profile_image = BlobField(null=True)
    licence_number = CharField(null=True, max_length=15)
    licence_image = BlobField(null=True)
    verified = BooleanField(default=False)
    mileage_card_number = CharField(null=True, max_length=15)

    class Meta:
        schema = schema_constant.transactional


class Equipments(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    type = EnumField(enum_class=EquipmentTypes)
    status = EnumField(enum_class=EquipmentStatus, default=EquipmentStatus.Active)
    serial_id = CharField(null=True)
    product_id = CharField(null=True)
    model_id = CharField(null=True)
    asset_id = CharField(null=True)

    class Meta:
        schema = schema_constant.transactional


class MobileOS(enum.Enum):
    Android = 'ANDROID'
    Ios = 'IOS'

    @staticmethod
    def from_str(string):
        if string in ['ANDROID']:
            return MobileOS.Android
        if string in ['IOS']:
            return MobileOS.Ios
        else:
            raise InvalidParameterError(description='Invalid Mobile OS',
                                        field_errors=[InvalidFieldError(FieldErrors.MobileOS)])


class MobileDevices(Equipments):
    device_token = CharField(max_length=150)
    os = EnumField(null=True, enum_class=MobileOS, max_length=20)
    os_version = CharField(null=True, max_length=20)
    brand = CharField(null=True)
    app_version = CharField(null=True, max_length=10)
    fcm_token = CharField(null=True)

    class Meta:
        schema = schema_constant.transactional


class Permissions(RawBaseModel):
    id = BigAutoField(primary_key=True)
    name = CharField(unique=True)  # format: can-create-resource, can-retrieve-update-big_resource
    description = CharField(null=True, max_length=100)
    resource_name = CharField(max_length=100)
    can_retrieve = BooleanField(default=False)  # allow to access some specific/limited record from the resources
    can_search = BooleanField(default=False)  # allow to access any record from the resources
    can_create = BooleanField(default=False)
    can_update = BooleanField(default=False)
    can_delete = BooleanField(default=False)

    class Meta:
        schema = schema_constant.authentication


RolePermissionRelDeferred = DeferredThroughModel()


# todo: can be replace directly with tables
class Resources(enum.Enum):
    Authorization = 'authorization'
    Users = 'users'
    Stations = 'stations'
    Wallets = 'wallets'
    Vehicles = 'vehicles'
    Bookings = 'bookings'
    VehicleMasters = 'vehicle_masters'
    ConfigMasters = 'config_masters'
    Services = 'services'
    Slots = 'slots'
    Notifications = 'notifications'
    Dashboard = 'dashboard'
    StationOverviewKpi = 'station-overview-kpi'
    StationServicePrice = 'station-service-price'
    StationEnergyConsumption = 'station-energy-consumption'
    Ratings = 'rating'


class PermissionScopes(enum.Enum):
    Create = 'create'
    Retrieve = 'retrieve'
    Update = 'update'
    Delete = 'delete'
    Search = 'search'


class Authorization:
    def __init__(self, resource, permissions):
        self.resource = resource
        self.permissions = permissions

    def __str__(self):
        return self.resource.value + "-" + self.permissions.value


# at the end this will Temporal
class Roles(RawBaseModel):
    id = BigAutoField(primary_key=True)
    name = EnumField(unique=True, enum_class=UserRoles)
    description = CharField(null=True, max_length=100)
    permissions = ManyToManyField(Permissions, through_model=RolePermissionRelDeferred)

    class Meta:
        schema = schema_constant.authentication


class RolePermissionRel(RawBaseModel):  # check if need to define columns or it will work
    role = ForeignKeyField(Roles, column_name='role_id', backref='permissions', lazy_load=False)
    permission = ForeignKeyField(Permissions, column_name='permission_id', lazy_load=False)

    class Meta:
        primary_key = CompositeKey('role', 'permission')
        schema = schema_constant.authentication


RolePermissionRelDeferred.set_model(RolePermissionRel)

RoleGroupRelDeferred = DeferredThroughModel()


class Groups(RawBaseModel):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=50)
    description = CharField(null=True, max_length=100)
    roles = ManyToManyField(Roles, through_model=RoleGroupRelDeferred)

    class Meta:
        schema = schema_constant.authentication


class GroupRoleRel(RawBaseModel):  # check if need to define columns or it will work
    group = ForeignKeyField(Groups, column_name='group_id', backref='roles', lazy_load=False)
    role = ForeignKeyField(Roles, column_name='role_id', lazy_load=False)

    class Meta:
        primary_key = CompositeKey('group', 'role')
        schema = schema_constant.authentication


RoleGroupRelDeferred.set_model(GroupRoleRel)


class UserGroupRel(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    user = ForeignKeyField(Users, column_name='user_record_id', lazy_load=False)
    group_id = ForeignKeyField(Groups, column_name='group_id', lazy_load=False)

    class Meta:
        schema = schema_constant.authentication


class AuthenticationState(enum.Enum):
    Unauthorized = 'UNAUTHENTICATED'
    OtpRequired = 'OTP_REQUIRED'
    OtpFailed = 'OTP_FAILED'
    OtpRestricted = 'OTP_RESTRICTED'
    Restricted = 'RESTRICTED'
    Discarded = 'DISCARDED'
    RefreshFailed = 'REFRESH_FAILED'
    Success = 'SUCCESS'
    OtpSendFailed = 'OTP_SEND_FAILED'


class AuthAttempts(BaseModel):
    txn_id = UUIDField(primary_key=True)
    phone_number = CharField(max_length=12)
    country_code = CharField(max_length=4, null=True)
    device_token = CharField(max_length=100)
    otp = CharField(max_length=6, null=True)
    state = EnumField(enum_class=AuthenticationState)
    state_desc = CharField(max_length=100)
    verification_attempt_count = IntegerField(default=0)
    gateway_send_otp_res_status = CharField(max_length=10, null=True)  # status code of sms gateway api call
    gateway_send_otp_res_body = BinaryJSONField()  # response of sms gateway api call
    claims_issued = CharField(null=True, max_length=100)  # todo: not sure what to put
    backing_txn_id = UUIDField(null=True)

    class Meta:
        schema = schema_constant.authentication


# todo: can combine user & device as uniqueness
class AuthenticatedSessions(TemporalBaseModel):
    id = UUIDField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    user = ForeignKeyField(Users, column_name='user_record_id', lazy_load=False)
    device_record_id = ForeignKeyField(MobileDevices, column_name='device_record_id', lazy_load=False)
    group_id = ForeignKeyField(Groups, column_name='group_id', lazy_load=False)
    relative_auth_attempt = ForeignKeyField(AuthAttempts, column_name='auth_attempt_id', lazy_load=False)

    class Meta:
        schema = schema_constant.authentication


class Visibility(enum.Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


class AppConfigs(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    key = CharField()
    value = CharField()
    visibility = EnumField(null=True, enum_class=Visibility)

    class Meta:
        schema = schema_constant.master

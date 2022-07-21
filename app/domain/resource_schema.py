import datetime
import enum
from datetime import timedelta

from peewee import BigAutoField, ForeignKeyField, CharField, BlobField, AutoField, IntegerField, BooleanField, \
    UUIDField, PrimaryKeyField, DecimalField, BitField, TimeField, DateField, FloatField, DateTimeField
from playhouse.postgres_ext import BinaryJSONField, IntervalField, ArrayField

from app.constant import schema_constant
from app.domain.auth_schema import Users, Accounts, Equipments, EquipmentTypes
from app.domain.base import TemporalBaseModel, BaseModel, EnumField, InfDateTimeField


class Units(enum.Enum):
    Watt = 'WATT'
    Minute = 'MINUTE'
    Car = 'CAR'
    Voltage = 'VOLTAGE'
    Ampere = 'AMPERE'
    Cng = 'CNG'


class ChargeTypes(enum.Enum):
    SlowCharge = 'SLOW_CHARGE'
    FastCharge = 'FAST_CHARGE'
    CNG = 'CNG'



class ChargingConnectors(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    name = CharField(max_length=100)
    icon_image = BlobField()
    standard_name = CharField(max_length=50)
    description = CharField(max_length=100)

    class Meta:
        schema = schema_constant.master


class VehicleMasters(TemporalBaseModel):
    id = AutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    brand = CharField(max_length=100)
    model = CharField(max_length=120)
    manufacturing_year = IntegerField()
    image = BlobField(null=True)
    wheels = IntegerField(default=4, null=True)
    charging_connector_record = ForeignKeyField(ChargingConnectors, column_name='charging_connector_record_id',
                                                lazy_load=False)
    swappable_battery = BooleanField(null=True)
    swappable_battery_count = IntegerField(null=True)
    class_of_vehicle = CharField(max_length=50, null=True)
    charging_connector_records = ArrayField(IntegerField,
                                            column_name='connector_record_ids')# TODO: rename column

    class Meta:
        schema = schema_constant.master


class Vehicles(TemporalBaseModel):
    id = UUIDField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    registration_number = CharField(max_length=50)
    registration_certificate_image = BlobField()
    registration_plate_number = CharField(null=True, max_length=20)
    verified = BooleanField(default=False)
    vehicle_master = ForeignKeyField(VehicleMasters, column_name='vehicle_master_id',
                                     lazy_load=False)  # have use primary key instead of record_id just to get value of selection time
    vehicle_master_json = BinaryJSONField()  # for debug purpose
    user_record = ForeignKeyField(Users, column_name='user_record_id', lazy_load=False)

    class Meta:
        schema = schema_constant.transactional


# no need to put primary owner into this table
class VehicleAuthorization(TemporalBaseModel):
    id = PrimaryKeyField()
    record_id = CharField()  # todo: do we require this? if yes it should be mixture of user+vehicle record_id
    user_record_id = ForeignKeyField(Users, field=Users.record_id)  # todo: or we should use ref to VehicleOwners table
    vehicle_record_id = ForeignKeyField(Vehicles, field=Vehicles.record_id)


class Stations(Accounts):
    station_code = CharField(max_length=120)  # rto number+sequence code
    name = CharField()
    location_latitude = DecimalField(max_digits=15, decimal_places=10)
    location_longitude = DecimalField(max_digits=15, decimal_places=10)
    address = CharField(null=True)
    pinCode = CharField(null=True, max_length=10)
    contact_number = CharField(null=True, max_length=12)
    website = CharField(null=True)
    verified = BooleanField(default=False)
    has_hygge_box = BooleanField(default=False, null=True)
    hygge_box_number = CharField(null=True, max_length=150)

    class Meta:
        schema = schema_constant.transactional


class StationAssignment(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id',
                                lazy_load=False)  # it should be mixture of user+station record_id, just a thought
    user_record_id = ForeignKeyField(Users, column_name='user_record_id',
                                     lazy_load=False)  # todo: or we should use ref to StationOwners table
    station_record_id = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    verified = BooleanField(default=False, null=True)  # todo: do we need this?

    class Meta:
        schema = schema_constant.transactional


class StationMedias(BaseModel):
    id = PrimaryKeyField()
    station_record = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False,
                                     backref='station_images')
    image = BlobField()
    image_rank = IntegerField(default=1)

    class Meta:
        schema = schema_constant.transactional


# can be optimized, use concept of defaults
class StationOperationDetails(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    station_record_id = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    operating_days = BitField()
    operation_start_time = TimeField()
    operation_end_time = TimeField()

    class Meta:
        schema = schema_constant.transactional

    is_monday_operational = operating_days.flag(1)
    is_tuesday_operational = operating_days.flag(2)
    is_wednesday_operational = operating_days.flag(4)
    is_thursday_operational = operating_days.flag(8)
    is_friday_operational = operating_days.flag(16)
    is_saturday_operational = operating_days.flag(32)
    is_sunday_operational = operating_days.flag(64)


# can be optimized, use concept of defaults
class StationOperatingTimeMaster(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    operation_type = CharField(max_length=20)  # operation_start or operation_end
    window_start_time = TimeField()
    window_end_time = TimeField()
    duration = IntervalField()
    time_offset = IntervalField(default=timedelta().min)

    class Meta:
        schema = schema_constant.master


# we will need more tables to manage holidays
class StationHolidays(BaseModel):
    id = PrimaryKeyField()
    date = DateField()
    station_record_id = ForeignKeyField(Stations, field=Stations.record_id)
    remark = CharField(max_length=50)


class RatedPowers(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    power = FloatField()
    power_unit = EnumField(enum_class=Units)
    charge_type = EnumField(enum_class=ChargeTypes)

    class Meta:
        schema = schema_constant.master


class EquipmentTypeMasters(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    name = CharField(max_length=100)
    type = EnumField(enum_class=EquipmentTypes)
    icon_image = BlobField()
    rank = IntegerField(default=1)
    description = CharField(null=True)

    class Meta:
        schema = schema_constant.master


# to follow equipments table id_seq for primary key
class Chargers(Equipments):
    name = CharField(null=True, max_length=150)
    rank = IntegerField(default=1)
    station_record = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)

    class Meta:
        schema = schema_constant.transactional


class Nozzles(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    charger_record = ForeignKeyField(Chargers, column_name='charger_record_id', lazy_load=False)
    charging_connector_record = ForeignKeyField(ChargingConnectors, column_name='charging_connector_record_id',
                                                lazy_load=False)
    rated_power_record = ForeignKeyField(RatedPowers, column_name='rated_power_record_id', lazy_load=False)
    asset_id = CharField(max_length=100, null=True)
    serial_id = CharField(null=True)
    vehicle_per_nozzle = IntegerField()

    class Meta:
        schema = schema_constant.transactional


class VerificationStatus(enum.Enum):
    Pending = 'PENDING'
    Verified = 'VERIFIED'
    Rejected = 'REJECTED'
    Expired = 'EXPIRED'  # todo: confirm if required


class Verifications(BaseModel):
    id = BigAutoField(primary_key=True)
    registrant_user = ForeignKeyField(Users, column_name='registered_by', lazy_load=False)
    registered_user = ForeignKeyField(Users, column_name='registered_user_record_id', lazy_load=False, null=True)
    registered_vehicle = ForeignKeyField(Vehicles, column_name='registered_vehicle_record_id', lazy_load=False,
                                         null=True)
    registered_station = ForeignKeyField(Stations, column_name='registered_station_record_id', lazy_load=False,
                                         null=True)
    verifier_user = ForeignKeyField(Users, column_name='verified_by', lazy_load=False, null=True)
    verification_time = DateTimeField(null=True)
    verification_status = EnumField(enum_class=VerificationStatus, default=VerificationStatus.Pending)
    verifier_remark = CharField(null=True)
    verification_expiry = InfDateTimeField(default=datetime.datetime.max, null=True)

    class Meta:
        schema = schema_constant.transactional


class StationOperationBreakDetails(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    station_record_id = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    break_days = BitField()
    break_start_time = TimeField()
    break_end_time = TimeField()
    description = CharField(500)

    is_monday_operational = break_days.flag(1)
    is_tuesday_operational = break_days.flag(2)
    is_wednesday_operational = break_days.flag(4)
    is_thursday_operational = break_days.flag(8)
    is_friday_operational = break_days.flag(16)
    is_saturday_operational = break_days.flag(32)
    is_sunday_operational = break_days.flag(64)

    class Meta:
        schema = schema_constant.transactional

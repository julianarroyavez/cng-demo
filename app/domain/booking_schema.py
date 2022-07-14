import datetime
import enum

from peewee import AutoField, TimeField, BlobField, BigAutoField, ForeignKeyField, DecimalField, IntegerField, \
    DateField, UUIDField, CharField, BooleanField
from playhouse.postgres_ext import HStoreField, ArrayField

from app.constant import schema_constant
from app.domain.auth_schema import Users
from app.domain.base import RawBaseModel, EnumField, TemporalBaseModel, BaseModel
from app.domain.payment_schema import Invoices, CurrencyUnit
from app.domain.resource_schema import Nozzles, Stations, Vehicles, Units, ChargeTypes


class ServiceTypes(enum.Enum):
    ValueAdd = 'VALUE_ADD'
    EvCharge = 'EV_CHARGE'
    BatteryCharge = 'BATTERY_CHARGE'
    BatterySwap = 'BATTERY_SWAP'
    Cng = 'CNG'


class CancellationRefundDuration(enum.Enum):
    FullRefund = 60
    Refund15min = 15


class SegmentsOfDayEnum(enum.Enum):
    Morning = 'MORNING'
    Afternoon = 'AFTERNOON'
    Evening = 'EVENING'
    Night = 'NIGHT'


class BookingStatus(enum.Enum):
    Booked = 'BOOKED'
    Cancelled = 'CANCELLED'
    Completed = 'COMPLETED'
    Missed = 'MISSED'
    Fulfilled = 'FULFILLED'
    UnderFulfillment = 'UNDER_FULFILLMENT'


class SegmentsOfDay(RawBaseModel):
    id = AutoField()
    name = CharField(max_length=20)
    key = EnumField(enum_class=SegmentsOfDayEnum)
    segment_start_time = TimeField()
    segment_end_time = TimeField()
    icon_image = BlobField()

    class Meta:
        schema = schema_constant.master


class ServiceMasters(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    primary = BooleanField(null=True)  # todo: use of this?
    name = CharField(max_length=100)
    type = EnumField(enum_class=ServiceTypes)
    description = CharField(max_length=150, null=True)
    service_rank = IntegerField(null=True)
    icon_image = BlobField(null=True)
    parameters = HStoreField(null=True)  # check if hstore doesn't work we have to create ServiceParameter table

    class Meta:
        schema = schema_constant.master


class ServiceRates(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    primary = BooleanField(null=True)  # to define default rate of service
    description = CharField(max_length=100)
    service_record = ForeignKeyField(ServiceMasters, column_name='service_master_record_id', lazy_load=False)

    class Meta:
        schema = schema_constant.master


class ServiceRateTable(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    description = CharField(null=True, max_length=30)
    consumption_unit = EnumField(enum_class=Units)
    consumption_from = DecimalField()
    consumption_to = DecimalField()
    rate = DecimalField()
    rate_unit = EnumField(enum_class=CurrencyUnit)
    covered_rated_powers = ArrayField(IntegerField)
    days_of_week = IntegerField()
    segments_of_day = ArrayField(IntegerField)
    service_rate = ForeignKeyField(ServiceRates, column_name='service_rate_id', null=True, lazy_load=False)

    class Meta:
        schema = schema_constant.master


class StationServices(TemporalBaseModel):
    id = BigAutoField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    station_record_id = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    service_master_record = ForeignKeyField(ServiceMasters, column_name='service_master_record_id', lazy_load=False)
    custom_service_rate_record = ForeignKeyField(ServiceRates, column_name='custom_service_rate_record_id', null=True, lazy_load=False)

    class Meta:
        schema = schema_constant.transactional


class Slots(BaseModel):
    id = BigAutoField(primary_key=True)
    nozzle = ForeignKeyField(Nozzles, column_name='nozzle_record_id', lazy_load=False)
    date = DateField()
    start_time = TimeField()
    end_time = TimeField()
    slot_number = CharField(null=True, max_length=15)
    status = CharField(null=True, max_length=15)  # todo: convert to enumfield

    class Meta:
        schema = schema_constant.transactional


class Bookings(BaseModel):
    booking_id = UUIDField(primary_key=True)
    consumer_user = ForeignKeyField(Users, column_name='consumer_user_record_id', lazy_load=False)
    vehicle = ForeignKeyField(Vehicles, column_name='vehicle_record_id', lazy_load=False)
    station = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    slot = ForeignKeyField(Slots, column_name='slot_id', lazy_load=False)
    booking_date = DateField(default=datetime.date.today())
    service_date = DateField()
    booking_status = EnumField(enum_class=BookingStatus)
    otp = CharField(max_length=10)
    qr_code_data = CharField()
    total_charges = DecimalField()
    cancellation_charges = DecimalField(null=True)
    deferred_transaction = ForeignKeyField(Invoices, column_name='deferred_txn_invoice_id', lazy_load=False, null=True)
    final_transaction = ForeignKeyField(Invoices, column_name='final_txn_invoice_id', lazy_load=False, null=True)
    charging_type = EnumField(enum_class=ChargeTypes)

    class Meta:
        schema = schema_constant.transactional


class DaySegments(RawBaseModel):
    id = AutoField()
    name = CharField(max_length=20)
    key = EnumField(enum_class=SegmentsOfDayEnum)
    segment_start_time = TimeField()
    segment_end_time = TimeField()
    icon_image = BlobField()

    class Meta:
        schema = schema_constant.master




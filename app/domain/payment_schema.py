import enum

from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, CharField, BigAutoField, UUIDField, DateField
from playhouse.postgres_ext import BinaryJSONField, HStoreField

from app.constant import schema_constant
from app.domain.auth_schema import Accounts, Equipments
from app.domain.base import TemporalBaseModel, BaseModel, EnumField


class CurrencyUnit(enum.Enum):
    Token = 'TOKEN'
    IndianRupee = 'INR'


# rate master
class TokenConversionRates(TemporalBaseModel):
    id = PrimaryKeyField()
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    conversion_rate = DecimalField()
    conversion_from_unit = CharField()  # rupees enum
    conversion_to_unit = CharField()  # tokens enum
    description = CharField(max_length=100, null=True)

    class Meta:
        schema = schema_constant.master


class OrderTypes(enum.Enum):
    PayForToken = 'PAY_FOR_TOKEN'
    PurchaseToken = 'PURCHASE_TOKEN'
    EncashToken = 'ENCASH_TOKEN'
    PayForBooking = 'PAY_FOR_BOOKING'
    CancelBooking = 'CANCEL_BOOKING'
    TransferToken = 'TRANSFER_TOKEN'


class Orders(BaseModel):
    order_id = CharField(max_length=50, primary_key=True)
    order_summary = CharField(max_length=100, null=True)
    total = DecimalField()  # sum of all items, ideally it would be one only
    order_status = CharField(max_length=10)  # pending, success, failure
    order_type = EnumField(enum_class=OrderTypes)

    class Meta:
        schema = schema_constant.payment


class OrderItems(BaseModel):
    id = BigAutoField(primary_key=True)
    item = CharField(max_length=100)  # token purchase
    item_rate = DecimalField(default=1)  # 1
    applied_token_rate = ForeignKeyField(TokenConversionRates, column_name='applied_token_rate', null=True)
    quantity = DecimalField()  # 50 amount
    total = DecimalField()  # item * quantity * conversion_rate
    order = ForeignKeyField(Orders, column_name='order_id', backref='order_items', lazy_load=False)
    attrs = HStoreField(null=True)  # todo: to store related service item refs

    class Meta:
        schema = schema_constant.payment


# use for both currency and tokens
class PaymentState(enum.Enum):
    Init = 'INIT'
    GatewayInitFailed = 'GATEWAY_INIT_FAILED'
    ProcessRequired = 'PROCESS_REQUIRED'
    VerificationFailed = 'VERIFICATION_FAILED'
    TxnCancelled = 'TXN_CANCELLED'
    TxnFailed = 'TXN_FAILED'
    Success = 'SUCCESS'


class Payments(BaseModel):
    id = UUIDField(primary_key=True)
    order = ForeignKeyField(Orders, column_name='order_id', lazy_load=False)  # todo: remove direct dependency from orders manage via invoice
    sender = ForeignKeyField(Accounts, column_name='sender', lazy_load=False)
    receiver = ForeignKeyField(Accounts, column_name='receiver', lazy_load=False)
    order_amount = DecimalField()  # todo: rename to transaction_amount
    order_date = DateField()  # todo: rename to transaction_date
    payment_status = EnumField(enum_class=PaymentState)
    # todo: introduce to understand the status
    gateway_response = BinaryJSONField()  # todo: 1.nullable=True 2.need to use it as map, key:value {status:jsonResponse}
    client_response = BinaryJSONField()  # todo: nullable=True
    device = ForeignKeyField(Equipments, column_name='device_id', null=True, lazy_load=False)
    gateway_name = CharField(null=True, max_length=50)
    comment = CharField(null=True, max_length=120)

    class Meta:
        schema = schema_constant.payment


#  1 order = 1 invoice, invoice before payment
class Invoices(BaseModel):
    id = BigAutoField(primary_key=True)
    invoice_number = UUIDField(unique=True)
    order = ForeignKeyField(Orders, column_name='order_id', lazy_load=False)
    comment = CharField(null=True, max_length=50)
    payment = ForeignKeyField(Payments, column_name='payment_id', lazy_load=False)
    attrs = HStoreField(null=True)  # use for mapping token txn with currency txn

    class Meta:
        schema = schema_constant.payment


# optimistic locking
# check archival
class Wallets(TemporalBaseModel):
    id = UUIDField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    account = ForeignKeyField(Accounts, column_name='account_id', lazy_load=False)
    name = CharField(null=True)
    balance = DecimalField(default=0)  # split into 2 - in_transit & actual_balance
    in_transit = DecimalField(null=True)

    class Meta:
        schema = schema_constant.payment

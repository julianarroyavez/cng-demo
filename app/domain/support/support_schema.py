import enum

from peewee import BigAutoField, CharField, IntegerField, UUIDField, DateField

from app.constant import schema_constant
from app.domain.base import BaseModel, EnumField
from app.log import LOG


class SupportSchemaModel(BaseModel):
    class Meta:
        schema = schema_constant.support


class ContentType(enum.Enum):
    Question = 'QUESTION'
    Answer = 'ANSWER'
    Category = 'CATEGORY'
    Action = 'ACTION'

    @staticmethod
    def from_str(string):
        if string == 'QUESTION':
            return ContentType.Question
        if string == 'ANSWER':
            return ContentType.Answer
        if string == 'CATEGORY':
            return ContentType.Category
        if string == 'ACTION':
            return ContentType.Action


class ContentFormat(enum.Enum):
    Text = 'TEXT'
    DeepLink = 'DEEPLINK'

    @staticmethod
    def from_str(string):
        if string == 'TEXT':
            return ContentFormat.Text
        if string == 'DEEPLINK':
            return ContentFormat.DeepLink


class SupportQueryStatus(enum.Enum):
    Open = 'OPEN'
    UnderResolution = 'UNDER_RESOLUTION'
    CustomerInputRequired = 'CUSTOMER_INPUT_REQUIRED'
    Resolved = 'RESOLVED'
    Discarded = 'DISCARDED'

    @staticmethod
    def get_active_query_status(status):
        try:
            status = status.split(',')
            result = [SupportQueryStatus.from_str(item) for item in status]
            return result
        except Exception as e:
            LOG.error(e)
            return [SupportQueryStatus.Open,
                    SupportQueryStatus.UnderResolution,
                    SupportQueryStatus.CustomerInputRequired,
                    SupportQueryStatus.Resolved,
                    SupportQueryStatus.Discarded]

    @staticmethod
    def from_str(string):
        if string == 'OPEN':
            return SupportQueryStatus.Open
        if string == 'UNDER_RESOLUTION':
            return SupportQueryStatus.UnderResolution
        if string == 'CUSTOMER_INPUT_REQUIRED':
            return SupportQueryStatus.CustomerInputRequired
        if string == 'RESOLVED':
            return SupportQueryStatus.Resolved
        if string == 'DISCARDED':
            return SupportQueryStatus.Discarded


class QueryState(enum.Enum):
    Restricted = 'RESTRICTED'
    Success = 'SUCCESS'


class SupportQueries(SupportSchemaModel):
    id = UUIDField(primary_key=True)
    status = EnumField(enum_class=SupportQueryStatus)
    query_text = CharField(max_length=600)
    customer_user = UUIDField(null=True)
    customer_phone = CharField(max_length=20)
    customer_email = CharField(max_length=50, null=True)
    customer_device_token = CharField(max_length=255)
    customer_device_os_version = CharField(max_length=255)
    customer_app_version = CharField(max_length=50)
    response_date = DateField(null=True)
    response_by = UUIDField(null=True)
    response_comment = CharField(max_length=600, null=True)
    session_token = CharField(max_length=10000, null=True)


class QueryAttempts(SupportSchemaModel):
    id = BigAutoField(primary_key=True)
    phone_number = CharField(max_length=12)
    device_token = CharField(max_length=100)
    state = EnumField(enum_class=QueryState)
    state_desc = CharField(max_length=100)


class FAQS(SupportSchemaModel):
    id = BigAutoField(primary_key=True)
    content_type = EnumField(enum_class=ContentType)
    content_text = CharField(max_length=600)
    content_format = EnumField(enum_class=ContentFormat)
    additional_text = CharField(max_length=600, null=True)
    parent_id = IntegerField(null=True)
    rank = IntegerField()


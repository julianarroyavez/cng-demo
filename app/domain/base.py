from typing import TypeVar

from peewee import DateTimeField, CharField, Model, BooleanField, DeferredForeignKey

from app.database import db_session
import datetime

T = TypeVar('T')


class InfDateTimeField(DateTimeField):
    def db_value(self, value):  # convert min max date values to infinity
        if value == datetime.datetime.max:
            return 'infinity'
        elif value == datetime.datetime.min:
            return '-infinity'
        else:
            return value


class EnumField(CharField):
    """
    This class enable a Enum like field for Peewee
    """
    def __init__(self, enum_class, max_length=50, *args, **kwargs):
        self.enum_class = enum_class
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.enum_class(value)


class RawBaseModel(Model):
    class Meta:
        database = db_session
        legacy_table_names = False


class BaseModel(RawBaseModel):
    active = BooleanField(default=True)
    created_on = DateTimeField(default=datetime.datetime.utcnow)
    created_by = DeferredForeignKey('users', column_name='created_by', null=False, lazy_load=False)  # can be used for attr based access check
    modified_on = DateTimeField(default=datetime.datetime.utcnow)
    modified_by = DeferredForeignKey('users', column_name='modified_by', null=False, lazy_load=False)

    class ColumnConfig:
        nullable_creation = False


class TemporalBaseModel(BaseModel):
    validity_start = DateTimeField(default=datetime.datetime.utcnow)
    validity_end = InfDateTimeField(default=datetime.datetime.max)

    @property
    def id(self):
        raise NotImplementedError

    @property
    def record_id(self):
        raise NotImplementedError

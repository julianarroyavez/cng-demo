from peewee import BigAutoField, DateTimeField, ForeignKeyField, IntegerField, CharField, BlobField, FloatField

from app.constant import schema_constant
from app.domain.auth_schema import Users
from app.domain.base import BaseModel
from app.domain.booking_schema import Bookings
from app.domain.resource_schema import Stations


class Ratings(BaseModel):
    id = BigAutoField(primary_key=True)
    rating_time = DateTimeField()
    rated_station = ForeignKeyField(Stations, column_name='rated_station', lazy_load=False, null=True)
    rated_by = ForeignKeyField(Users, column_name='rated_by', lazy_load=False, null=False)
    rated_booking = ForeignKeyField(Bookings, column_name='rated_booking', lazy_load=False, null=True)
    rating_value = IntegerField(null=False)
    rating_explanation = CharField(max_length=250, null=True)

    class Meta:
        schema = schema_constant.transactional


class StationStatistics(BaseModel):
    id = BigAutoField(primary_key=True)
    rated_station = ForeignKeyField(Stations, column_name='rated_station', lazy_load=False, null=False)
    average_rating_value = FloatField()
    rating_count = IntegerField()
    min_rating = IntegerField(default=1, null=True)
    max_rating = IntegerField(null=True)

    class Meta:
        schema = schema_constant.analytics


class RatingAttachments(BaseModel):
    id = BigAutoField(primary_key=True)
    rating_id = ForeignKeyField(Ratings, column_name='rating_id', lazy_load=False, null=False)
    attachment = BlobField()

    class Meta:
        schema = schema_constant.transactional

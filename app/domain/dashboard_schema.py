import enum

from peewee import DateField, ForeignKeyField, IntegerField, BigAutoField, CharField, TimeField, FloatField

from app.constant import schema_constant
from app.domain.base import BaseModel, TemporalBaseModel
from app.domain.resource_schema import Stations


class EnergyUnit(enum.Enum):
    kilowatt_hour = 'kwh'


class DashBoardReport(enum.Enum):
    station_overview_kpi = 'STATION_OVERVIEW_KPI'
    station_service_price = 'STATION_SERVICE_PRICE'
    station_energy_consumption = 'STATION_ENERGY_CONSUMPTION'


class EnergyConsumption(BaseModel):
    id = BigAutoField(primary_key=True)
    reading_date = DateField()
    reading_time = TimeField()
    station_client_code = CharField(max_length=50)
    grid_power = FloatField()
    solar_power = FloatField()
    diesel_generated_power = FloatField()
    total_power = FloatField()
    battery_charge = FloatField()
    battery_discharge = FloatField()
    charger_code = CharField(max_length=255)
    reading_duration = IntegerField()
    battery_soc = FloatField(column_name='battery_soc')

    class Meta:
        schema = schema_constant.telemetry


class StationMapping(TemporalBaseModel):
    id = BigAutoField(primary_key=True)
    record_id = ForeignKeyField('self', column_name='record_id', lazy_load=False)
    station_record_id = ForeignKeyField(Stations, column_name='station_record_id', lazy_load=False)
    station_client_code = CharField(max_length=50, null=True)

    class Meta:
        schema = schema_constant.telemetry

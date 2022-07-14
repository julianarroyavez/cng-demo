from peewee import fn

from app.domain.dashboard_schema import EnergyConsumption, StationMapping


class EnergyConsumptionRepository:

    def fetch_all_by_station_id_by_date(self, station_id, min_date, max_date):
        return (EnergyConsumption.select(
            EnergyConsumption.reading_date,
            (fn.Sum(EnergyConsumption.solar_power)/4).alias('sum_of_solar_power'),
            (fn.Sum(EnergyConsumption.grid_power)/4).alias('sum_of_grid_power'),
            (fn.Sum(EnergyConsumption.diesel_generated_power)/4).alias('sum_of_dg_power')
        ).join(StationMapping,
               on=EnergyConsumption.station_client_code == StationMapping.station_client_code
               ).distinct().where(
            (StationMapping.station_record_id == station_id)
            & (EnergyConsumption.reading_date >= min_date)
            & (EnergyConsumption.reading_date <= max_date)
        ).group_by(EnergyConsumption.reading_date).order_by(EnergyConsumption.reading_date))

    def fetch_all_by_station_id_by_month(self, station_id, min_date, max_date):
        return (EnergyConsumption.select(
            (fn.Sum(EnergyConsumption.solar_power)/4).alias('sum_of_solar_power'),
            (fn.Sum(EnergyConsumption.grid_power)/4).alias('sum_of_grid_power'),
            (fn.Sum(EnergyConsumption.diesel_generated_power)/4).alias('sum_of_dg_power')
        ).join(StationMapping,
               on=EnergyConsumption.station_client_code == StationMapping.station_client_code
               ).where(
            (StationMapping.station_record_id == station_id)
            & (EnergyConsumption.reading_date >= min_date)
            & (EnergyConsumption.reading_date <= max_date)
        )).get()

    def fetch_date_of_first_available_data(self):
        return EnergyConsumption.select(fn.MIN(EnergyConsumption.reading_date)).scalar()

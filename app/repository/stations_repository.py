import operator
import uuid
from functools import reduce

from peewee import fn

from app.database import db_session
from app.domain.auth_schema import AccountType
from app.domain.booking_schema import StationServices, ServiceMasters, ServiceRates, ServiceRateTable
from app.domain.rating.rating_schema import StationStatistics
from app.domain.resource_schema import Stations, Nozzles, Chargers, StationMedias, RatedPowers, StationOperationDetails, \
    ChargeTypes
from app.log import LOG
from app.repository.accounts_repository import AccountsRepository
from app.repository.station_mapping_repository import StationMappingRepository
from app.repository.wallets_repository import WalletsRepository


class StationsRepository:
    def insert(self, station_code, name, location_latitude, location_longitude, address, pin_code, contact_number,
               website, verified, has_hygge_box, req_auth_claims):
        LOG.info('inside station repo')
        with db_session.atomic():
            newly_added_station = (Stations
                                   .create(id=station_code,
                                           record_id=station_code,
                                           station_code=station_code,
                                           alias_name='Test-User',
                                           name=name,
                                           created_by=req_auth_claims.get('user'),
                                           modified_by=req_auth_claims.get('user'),
                                           location_latitude=location_latitude,
                                           location_longitude=location_longitude,
                                           address=address,
                                           pinCode=pin_code,
                                           contact_number=contact_number,
                                           website=website,
                                           verified=verified,
                                           has_hygge_box=has_hygge_box,
                                           type=AccountType.Station))

            AccountsRepository().insert(primary_key=station_code,
                                        record_id=station_code,
                                        alias_name='station_{}'.format(contact_number),
                                        creator_user_id=req_auth_claims.get('user'),
                                        now=newly_added_station.validity_start,
                                        type=AccountType.Station)

            wallet_key = str(uuid.uuid4())
            WalletsRepository().insert(primary_key=wallet_key,
                                       record_id=wallet_key,
                                       name='station_wallet_{}'.format(contact_number),
                                       account_id=station_code,
                                       creator_user_id=req_auth_claims.get('user'),
                                       now=newly_added_station.validity_start)
            StationMappingRepository().insert(
                station_record_id=newly_added_station.record_id,
                user=req_auth_claims.get('user')
            )

    def select_all_stations(self, now):
        return (Stations
                .select()
                .where((Stations.validity_start <= now)
                       & (Stations.validity_end > now)))

    def fetch_nearby_stations(self, lat, lon, radius, unit, now, where_clauses):
        fn_station_distance = fn.calculate_distance(Stations.location_latitude, Stations.location_longitude, lat, lon,
                                                    unit)
        return (Stations
                .select(Stations.record_id, Stations.station_code, Stations.name, Stations.address,
                        Stations.contact_number, Stations.website, Stations.location_latitude,
                        Stations.location_longitude, Stations.pinCode,
                        StationStatistics.average_rating_value, StationStatistics.rating_count,
                        fn_station_distance.alias('distance'))
                .join_from(Stations, Chargers, attr='chargers',
                           on=((Stations.record_id == Chargers.station_record)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)
                               & (fn.calculate_distance(Stations.location_latitude, Stations.location_longitude, lat,
                                                        lon, unit) < radius)))
                .join_from(Chargers, Nozzles, attr='nozzles',
                           on=((Chargers.record_id == Nozzles.charger_record)
                               & (Nozzles.validity_start <= now)
                               & (Nozzles.validity_end > now)))
                .join_from(Nozzles, RatedPowers, attr="rated_powers",
                           on=(Nozzles.rated_power_record_id == RatedPowers.record_id))
                .join_from(Stations, StationStatistics, attr='station_stat',
                           on=(Stations.record_id == StationStatistics.rated_station))
                .where(reduce(operator.and_, where_clauses))
                .order_by(fn_station_distance))

    def fetch_by_record_id(self, now, station_id):
        return (Stations
                .select()
                .where((Stations.validity_start <= now)
                       & (Stations.validity_end > now)
                       & (Stations.record_id == station_id)))

    def fetch_for_charging_connectors(self, station_list, now=None):
        return (Stations
                .select(Stations.record_id, Nozzles.charging_connector_record)
                .join_from(Stations, Chargers, attr='chargers',
                           on=((Stations.record_id == Chargers.station_record)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .join_from(Chargers, Nozzles, attr='nozzles',
                           on=((Chargers.record_id == Nozzles.charger_record)
                               & (Nozzles.validity_start <= now)
                               & (Nozzles.validity_end > now)))
                .where(Stations.record_id.in_(station_list))
                .group_by(Stations.record_id, Nozzles.charging_connector_record))

    def fetch_for_rated_powers(self, station_list, now=None):
        return (Stations
                .select(Stations.record_id, Nozzles.charging_connector_record, RatedPowers.record_id,
                        RatedPowers.charge_type)
                .join_from(Stations, Chargers, attr='chargers',
                           on=((Stations.record_id == Chargers.station_record)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .join_from(Chargers, Nozzles, attr='nozzles',
                           on=((Chargers.record_id == Nozzles.charger_record)
                               & (Nozzles.validity_start <= now)
                               & (Nozzles.validity_end > now)))
                .join_from(Nozzles, RatedPowers, attr="rated_powers",
                           on=((Nozzles.rated_power_record_id == RatedPowers.record_id)
                               & (Nozzles.validity_start <= now)
                               & (Nozzles.validity_end > now))).where(Stations.record_id.in_(station_list)))

    def fetch_for_media(self, station_list):
        return (Stations
                .select(Stations.record_id, StationMedias.id, StationMedias.image_rank)
                .join_from(Stations, StationMedias, attr='media',
                           on=(Stations.record_id == StationMedias.station_record))
                .where(Stations.record_id.in_(station_list)))

    def fetch_for_thumbnails(self, station_list):
        return (StationMedias
                .select(StationMedias.id, StationMedias.station_record)
                .where((StationMedias.image_rank == 1)
                       & (StationMedias.station_record.in_(station_list))))

    def fetch_all_ids_by_charging_connectors(self, station_list, charging_connector_id, now):
        return (Stations
                .select(Stations.record_id, Nozzles.charging_connector_record)
                .join_from(Stations, Chargers, attr='chargers',
                           on=((Stations.record_id == Chargers.station_record)
                               & (Chargers.validity_start <= now)
                               & (Chargers.validity_end > now)))
                .join_from(Chargers, Nozzles, attr='nozzles',
                           on=((Chargers.record_id == Nozzles.charger_record)
                               & (Nozzles.validity_start <= now)
                               & (Nozzles.validity_end > now)))
                .where((Stations.validity_start <= now)
                       & (Stations.validity_end > now)
                       & (Stations.record_id.in_(station_list))
                       & (Nozzles.charging_connector_record == charging_connector_id))
                .group_by(Stations.record_id, Nozzles.charging_connector_record))

    def fetch_image_by_id_and_station_id(self, station_id, image_id):
        return (StationMedias
                .select(StationMedias.image)
                .where((StationMedias.id == image_id)
                       & (StationMedias.station_record == station_id))
                .get()
                .image)

    def fetch_all_service_master_by_station(self, now, station_id):
        return Stations.select(
            Stations.record_id,
            StationOperationDetails.operating_days,
            StationOperationDetails.operation_start_time,
            StationOperationDetails.operation_end_time,
            ServiceMasters.name,
            ServiceMasters.type,
            ServiceMasters.id,
            ServiceMasters.parameters
        ).join(StationOperationDetails,
               on=((StationOperationDetails.station_record_id == Stations.record_id)
                   & (StationOperationDetails.validity_start <= now)
                   & (StationOperationDetails.validity_end > now))) \
            .join(StationServices,
                  on=((StationServices.station_record_id == Stations.record_id)
                      & (StationServices.validity_start <= now)
                      & (StationServices.validity_end > now))) \
            .join(ServiceMasters,
                  on=((ServiceMasters.id == StationServices.service_master_record)
                      & (ServiceMasters.validity_start <= now)
                      & (ServiceMasters.validity_end > now))) \
            .join(Chargers,
                  on=((Chargers.station_record == StationServices.station_record_id)
                      & (Chargers.validity_start <= now)
                      & (Chargers.validity_end > now))) \
            .join(ServiceRates,
                  on=((ServiceRates.id == StationServices.custom_service_rate_record)
                      & (ServiceRates.validity_start <= now)
                      & (ServiceRates.validity_end > now))) \
            .join(ServiceRateTable,
                  on=((ServiceRateTable.service_rate == ServiceRates.id)
                      & (ServiceRateTable.validity_start <= now)
                      & (ServiceRateTable.validity_end > now))) \
            .distinct().where(
            (Stations.record_id == station_id)
            & (Stations.validity_start <= now)
            & (Stations.validity_end > now)
            & (ServiceMasters.parameters.contains({'charging_type': ChargeTypes.FastCharge.value})
               | ServiceMasters.parameters.contains({'charging_type': ChargeTypes.SlowCharge.value}
                                                    ))
        ).dicts()

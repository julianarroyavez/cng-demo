from app import log
from app.domain.resource_schema import Stations, Nozzles, Chargers
from app.util.datetime_util import datetime_now

LOG = log.get_logger()


class StationsWithConnectorType:

    def station_filter_query(self, id_list):
        now = datetime_now()

        station_query = Stations.select(
            Stations.record_id  # , Nozzles.charging_connector_record_id
        ).join_from(
            Stations, Chargers, attr='chargers',
            on=((Stations.record_id == Chargers.station_record_id)
                & (Chargers.validity_start <= now)
                & (Chargers.validity_end > now))
        ).join_from(
            Chargers, Nozzles, attr='nozzles',
            on=((Chargers.record_id == Nozzles.charger_record_id)
                & (Nozzles.validity_start <= now)
                & (Nozzles.validity_end > now))
        ).where((Stations.validity_start <= now)
                & (Stations.validity_end > now)
                # & (Nozzles.charging_connector_record_id == connector_type)
                & (Stations.record_id.in_(id_list))
                ).group_by(
            Stations.record_id, Nozzles.charging_connector_record_id
        )

        list_of_stations = []

        for station in station_query:
            list_of_stations.append(str(station.record_id))
        LOG.info('list_of_stations %s' % list_of_stations)
        return list_of_stations

    def connector_filter_query(self, list_of_stations):
        now = datetime_now()

        connector_type_query = Stations.select(
            Stations.record_id, Nozzles.charging_connector_record_id
        ).join_from(
            Stations, Chargers, attr='chargers',
            on=((Stations.record_id == Chargers.station_record_id)
                & (Chargers.validity_start <= now)
                & (Chargers.validity_end > now))
        ).join_from(
            Chargers, Nozzles, attr='nozzles',
            on=((Chargers.record_id == Nozzles.charger_record_id)
                & (Nozzles.validity_start <= now)
                & (Nozzles.validity_end > now))
        ).where((Stations.validity_start <= now)
                & (Stations.validity_end > now)
                # & (Nozzles.charging_connector_record_id == connector_type)
                & (Stations.record_id.in_(list_of_stations))
                ).group_by(
            Stations.record_id, Nozzles.charging_connector_record_id
        )
        list_of_connectors_with_stations_ids = {}

        for connector in connector_type_query:
            connectors = {
                "id": connector.chargers.nozzles.charging_connector_record
            }
            LOG.info(type(connectors))
            if connector.record_id not in list(list_of_connectors_with_stations_ids):
                list_of_connectors_with_stations_ids[connector.record_id] = connectors
            else:
                list_of_connectors_with_stations_ids[connector.record_id] = \
                    list_of_connectors_with_stations_ids[connector.record_id].get(connector.record_id, []).extend(connectors)
        LOG.info('list_of_connectors %s' % list_of_connectors_with_stations_ids)

        return list_of_connectors_with_stations_ids

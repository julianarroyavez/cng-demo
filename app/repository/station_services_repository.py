from peewee import fn
from app.domain.booking_schema import StationServices

from app.log import LOG


class StationServicesRepository:
    def insert(self, station_record_id, service_master_record, req_auth_claims, custom_service_rate_record_id):
        LOG.info('adding services')
        return StationServices.create(record_id=fn.currval('station_services_id_seq'),
                                      station_record_id=station_record_id,
                                      service_master_record=service_master_record,
                                      custom_service_rate_record=custom_service_rate_record_id,
                                      created_by=req_auth_claims.get('user'),
                                      modified_by=req_auth_claims.get('user'))

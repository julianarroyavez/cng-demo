from app.log import LOG
from app.service.charging_connector_service import ChargingConnectorService
from app.service.day_segment_service import SegmentOfDayService
from app.service.equipment_service import EquipmentService
from app.service.equipments_service import EquipmentTypeMasterService
from app.service.operating_time_masters_service import OperatingTimeMastersService
from app.service.permissions_service import PermissionsService
from app.service.rated_power_service import RatedPowerService
from app.service.service_master_service import ServiceMasterService
from app.service.slot_duration_service import SlotDurationService
from app.service.station_service import StationService
from app.service.user_service import UserService
from app.service.vehicle_service import VehicleService
from app.service.wallet_service import WalletService


def __embed_entity_stub(_, __, ___):
    LOG.warn("into __embed_entity_stub()")


__entity_function_dict = {
    'users': UserService().embed_user,
    'vehicles': VehicleService().embed_vehicles,
    'rated-powers': RatedPowerService().embed_rated_powers,
    'day-segments': SegmentOfDayService().embed_segments_of_day,
    'slot-durations': SlotDurationService().embed_slot_durations,
    'charging-connectors': ChargingConnectorService().embed_charging_connectors,
    'wallets': WalletService().embed_wallet,
    'operating-time-masters': OperatingTimeMastersService().embed_operating_time_masters,
    'stations': StationService().embed_stations,
    'services': ServiceMasterService().embed_master_service,
    'equipment-type-masters': EquipmentTypeMasterService().embed_equipment_types,
    'equipments': EquipmentService().embed_equipments,
    'permissions': PermissionsService().embed_permissions
}


def embed_entity_service_factory(entity):
    LOG.debug('embedding.. {}'.format(entity))
    return __entity_function_dict[entity] if entity in __entity_function_dict else __embed_entity_stub

import falcon

from app.domain.booking_schema import DaySegments
from app.domain.notification_schema import Notifications
from app.domain.dashboard_schema import EnergyConsumption, StationMapping
from app.domain.resource_schema import StationOperationBreakDetails
from app.domain.rating.rating_schema import Ratings, StationStatistics, RatingAttachments
from app.domain.support.support_schema import SupportQueries, QueryAttempts, FAQS
from app.middleware.api_logging_middleware import RequestLogging
from app.middleware.db_connection_middleware import DbSessionManager
from app.middleware.json_parser_middleware import JsonParser
from falcon_multipart.middleware import MultipartMiddleware
from app.middleware.authorization_middleware import AuthorizationMiddleware
from app.database import init_session, db_session
from app import query_debugging, log
from app.errors import AppError
from app.api.v1 import authenticate_resource, config_master_resource, service_resource, slot_resource, booking_resource, \
    app_config_resource, segment_of_day_resource, charging_connector_resource, equipment_resource, \
    mobile_device_resource, report_resource, notification_resource, query_resource, faq_resource, ratings_resource, \
    navigation_resource
from app.api.v1 import station_resource
from app.api.v1 import user_resource
from app.api.v1 import vehicle_master_resource
from app.api.v1 import vehicle_resource
from app.api.v1 import station_resource
from app.api.v1 import wallet_resource
from app.database import init_session
from app.errors import AppError
from app.middleware.api_logging_middleware import RequestLogging
from app.middleware.authorization_middleware import AuthorizationMiddleware
from app.middleware.db_connection_middleware import DbSessionManager
from app.middleware.json_parser_middleware import JsonParser

LOG = log.get_logger()


class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info("API server is starting..")

        self.add_route("/api/v1/app-configs", app_config_resource.Collection())
        self.add_route("/api/v1/authn", authenticate_resource.Collection())
        self.add_route("/api/v1/authn/{txn_id_path}/verify", authenticate_resource.ItemVerify())

        self.add_route("/api/v1/bookings", booking_resource.Collection())
        self.add_route("/api/v1/bookings/{booking_id}", booking_resource.Item())
        self.add_route("/api/v1/bookings/{booking_id}/cancel", booking_resource.CancelBooking())
        self.add_route("/api/v1/bookings/{booking_id}/penalties", booking_resource.CancelBookingPenalties())
        self.add_route("/api/v1/bookings/{booking_id}/ratings", booking_resource.RatingCollection())
        self.add_route("/api/v1/bookings/{booking_id}/send-fulfilled-notification",
                       booking_resource.NotificationPopupCollection())

        self.add_route("/api/v1/charging-connectors/{connector_id}/icon-image",
                       charging_connector_resource.ItemIconImage())
        self.add_route("/api/v1/config-masters", config_master_resource.Collection())

        self.add_route("/api/v1/day-segments/{segment_id}/icon-image", segment_of_day_resource.ItemIconImage())

        self.add_route("/api/v1/equipments/bulk", equipment_resource.BulkCollection())
        self.add_route("/api/v1/equipment-type-masters/{icon_id}/icon-image", equipment_resource.ItemIconImage())

        self.add_route("/api/v1/faqs", faq_resource.Collection())

        self.add_route("/api/v1/mobile-devices", mobile_device_resource.Collection())

        self.add_route("/api/v1/navigation", navigation_resource.Collection())
        self.add_route("/api/v1/notifications", notification_resource.Collection())
        self.add_route("/api/v1/notifications/bulk", notification_resource.BulkCollection())

        self.add_route("/api/v1/reports", report_resource.Collection())
        self.add_route("/api/v1/reports/station-service-price", report_resource.ItemPriceTableReport())
        self.add_route("/api/v1/reports/station-overview-kpi", report_resource.ItemKpiReport())
        self.add_route("/api/v1/reports/station-overview-kpi/kpis/kpi-total-charging-duration/icon-image",
                       report_resource.ItemKpiReport())
        self.add_route("/api/v1/reports/station-energy-consumption", report_resource.ItemEnergyConsumptionStats())

        self.add_route("/api/v1/services", service_resource.Collection())
        self.add_route("/api/v1/services/{service_id}/icon-image", service_resource.ItemIconImage())
        self.add_route("/api/v1/slots", slot_resource.Collection())
        self.add_route("/api/v1/stations", station_resource.Collection())
        self.add_route("/api/v1/stations/{station_id}/images/{image_id}", station_resource.ItemImage())
        self.add_route("/api/v1/stations/{station_id}/ratings", station_resource.RatingCollection())
        self.add_route("/api/v1/support-queries", query_resource.Collection())
        self.add_route("/api/v1/support-queries/{query_id}", query_resource.UpdateCollection())

        self.add_route("/api/v1/users", user_resource.Collection())
        self.add_route("/api/v1/users/{user_id}/verify", user_resource.ItemVerify())
        self.add_route("/api/v1/users/{user_id}/driving-licence-image", user_resource.ItemDLImage())
        self.add_route("/api/v1/users/{user_id}/profile-image", user_resource.ItemProfileImage())
        self.add_route("/api/v1/users/self", user_resource.Self())

        self.add_route("/api/v1/vehicle-masters", vehicle_master_resource.Collection())
        self.add_route("/api/v1/vehicle-masters/{vehicle_master_id}/model-image",
                       vehicle_master_resource.ItemModelImage())
        self.add_route("/api/v1/vehicles", vehicle_resource.Collection())
        self.add_route("/api/v1/vehicles/{vehicle_id}/verify", vehicle_resource.ItemVerify())
        self.add_route("/api/v1/vehicles/{vehicle_id}/certificate-image", vehicle_resource.ItemCertificateImage())
        self.add_route("/api/v1/vehicles/self", vehicle_resource.Self())

        self.add_route("/api/v1/wallets/self", wallet_resource.Self())
        self.add_route("/api/v1/wallets/self/purchase", wallet_resource.SelfPurchase())
        self.add_route("/api/v1/wallets/self/purchase/{txn_id}/verify", wallet_resource.SelfPurchaseVerify())
        self.add_route("/api/v1/wallets/self/transfer", wallet_resource.TransferTokens())
        self.add_route("/api/v1/wallets/self/encash", wallet_resource.SelfEncash())
        self.add_route("/api/v1/wallets/self/transactions", wallet_resource.Transaction())

        self.add_error_handler(Exception, AppError.handle_raw)
        self.add_error_handler(AppError, AppError.handle)


#init_session()
#db_session.connect()
#db_session.create_tables(
 #   [
        # AuthAttempts
        # Accounts, Users, Wallets
        # Equipments, MobileDevices,
        # Permissions, Roles, Groups, RolePermissionRel, GroupRoleRel, UserGroupRel,
        # AuthenticatedSessions,
        # ChargingConnectors, VehicleMasters, Vehicles,
        # Stations
        # StationAssignment, StationOperationDetails, StationOperatingTimeMaster
        # StationOperationBreakDetails
        # StationMedias, RatedPowers, Chargers, Nozzles
        # SegmentsOfDay,
        # Slots
        # Invoices, Bookings
        # ServiceMasters, ServiceRateTable, ServiceRates, StationServices
        # ServiceMasters, ServiceRateTable, ServiceRates, StationServices
        # TokenConversionRates, Orders, OrderItems,
        # Payments,
        # AppConfigs, Verifications
        # Notifications
        # EnergyConsumption,
        # StationMapping,
        # SupportQueries,
        # QueryAttempts,
        # StationOperationBreakDetails,
        # Ratings, StationStatistics, RatingAttachments
     #   DaySegments
    # ])
# db_session.close()
middlewares = [AuthorizationMiddleware(), MultipartMiddleware(), JsonParser(), RequestLogging(), DbSessionManager()]
application = App(middleware=middlewares)

if __name__ == '__main__':
    import os
    import waitress

    waitress.serve(application, host=os.getenv('MYAPI_WSGI_HOST', '192.168.31.6'),
                       port=os.getenv('MYAPI_WSGI_PORT', '8000'))

    from wsgiref.simple_server import make_server

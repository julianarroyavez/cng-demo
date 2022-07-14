import enum

import falcon

from app.api.common import BaseResource
from app.constant import dashboard_constant
from app.domain.auth_schema import Resources, PermissionScopes, Authorization
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.reports.report_service import ReportService


error_message = 'failed to get report details'
auth_claims = 'auth_claims'
user = 'user'


class Collection(BaseResource):
    class QueryParams(enum.Enum):
        ReportKeys = 'report-key'
        Date = 'date'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Dashboard, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = ReportService()
            body = service.get_dashboard_cards(
                report_key=self.QueryParams.ReportKeys.val(req),
                date=self.QueryParams.Date.val(req),
                user_record_id=req.context[auth_claims].get(user, None),
                station_id=req.context[auth_claims].get(dashboard_constant.STATION_ID, None)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message,
                                                                         raw_exception=e))


class ItemPriceTableReport(BaseResource):
    class QueryParams(enum.Enum):
        Date = 'date'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Dashboard, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = ReportService()
            body = service.get_report_price_table_data(
                date=self.QueryParams.Date.val(req),
                station_id=req.context[auth_claims].get(dashboard_constant.STATION_ID, None)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message,
                                                                         raw_exception=e))


class ItemKpiReport(BaseResource):
    class QueryParams(enum.Enum):
        Date = 'date'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Dashboard, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = ReportService()
            body = service.get_station_overview_kpi_report_data(
                date=self.QueryParams.Date.val(req),
                station_id=req.context[auth_claims].get(dashboard_constant.STATION_ID, None)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message,
                                                                         raw_exception=e))


class ItemEnergyConsumptionStats(BaseResource):

    class QueryParams(enum.Enum):
        DateFrom = 'date-from'
        DateTill = 'date-till'

        def val(self, req):
            return req.get_param(self.value)

    @falcon.before(authorize, [Authorization(Resources.Dashboard, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = ReportService()
            body = service.get_station_energy_consumption_statistics(
                date_from=self.QueryParams.DateFrom.val(req),
                date_till=self.QueryParams.DateTill.val(req),
                station_id=req.context[auth_claims].get(dashboard_constant.STATION_ID, None)
            )

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res,
                          e if isinstance(e, AppError) else UnknownError(description=error_message,
                                                                         raw_exception=e))

REPORT_KEY = 'reportKey'
DATE = 'date'
STATION_SERVICE_PRICE_DATA = 'station-service-price'
STATION_OVERVIEW_KPI = 'station-overview-kpi'
STATION_ENERGY_CONSUMPTION_GRAPH = 'station-energy-consumption'
STATION_SERVICE_PRICE_DATA_API_URL = 'api/v1/reports/station-service-price?date=%s'
DATA_TABLE = 'DATA_TABLE'
STATION_OVERVIEW_KPI_API_URL = 'api/v1/reports/station-overview-kpi?date=%s'
OVERVIEW_TITLE = 'OVERVIEW'
KPI_LIST = 'KPI_LIST'
PRICE_TABLE_TITLE = 'TODAY\'S PRICING'
STATION_STATISTICS_GROUP_API_URL = 'api/v1/reports/station-statistics-group?date=%s'
STATION_STATISTICS_GROUP = 'station-statistics-group'
REPORT_GROUP = 'REPORT_GROUP'
STATION_ENERGY_CONSUMPTION_GRAPH_API_URL = 'api/v1/reports/station-energy-consumption?date-from=%s&date-till=%s'
ENERGY_CONSUMPTION_TITLE = 'ENERGY CONSUMPTION'
STATS_GRAPH = 'STATS_GRAPH'
STATION_ID = 'station_id'
FAST_DC = 'Fast DC'
SLOW_DC = 'Slow AC'
CAR_WASH = 'Car Wash'
SLOW_EV_CHARGING = 'SLOW_CHARGE'
FAST_EV_CHARGING = 'FAST_CHARGE'
DURATION_15_MIN = '15min'
DURATION_30_MIN = '30min'
DURATION_60_MIN = '60min'
MINUTES = 'MINUTES'
SLOW_EV_CHARGING_SUB_TYPE = 'slow_ev_charge'
FAST_EV_CHARGING_SUB_TYPE = 'fast_ev_charge'
CAR_WASH_SUB_TYPE = 'car_wash'
RECORD_ID = 'record_id'
NAME = 'name'
TYPE = 'type'
ID = 'id'
TOKEN = 'TOKEN'
TREND_UPWARDS = 'UP'
TREND_DOWNWARDS = 'DOWN'
TREND_NONE = 'NONE'
CHARGING_DURATION_TITLE = 'Total Charging Duration'
ENERGY_CONSUMED_TITLE = 'Energy Consumed'
NO_OF_BOOKING_TITLE = 'No. of Bookings'
OUTAGES_TITLE = 'Outages'
CHARGING_DURATION_KEY = 'kpi-total-charging-duration'
ENERGY_CONSUMED_KEY = 'kpi-total-energy-consumption'
NO_OF_BOOKING_KEY = 'kpi-booking-count'
OUTAGES_KEY = 'kpi-outages'
CHARGING_DURATION_URL = 'api/v1/reports/station-overview-kpi/kpis/kpi-total-charging-duration/icon-image'
NO_OF_BOOKING_URL = 'api/v1/reports/station-overview-kpi/kpis/kpi-booking-count/icon-image'
ENERGY_CONSUMED_URL = 'api/v1/reports/station-overview-kpi/kpis/kpi-total-energy-consumption/icon-image'
OUTAGES_URL = 'api/v1/reports/station-overview-kpi/kpis/kpi-outages/icon-image'

PRICE_TABLE_RATES_QUERY_FOR_EACH_SERVICE = 'select distinct srt.consumption_from, srt.consumption_to, srt.consumption_unit, srt.rate, ' \
                                           'unnest(srt.segments_of_day) as segment_of_day, ' \
                                           'sm.id as service_master_id, sm.name, sm.type, s.record_id, ' \
                                           'sm.parameters -> \'charging_type\' as sub_type ' \
                                           'from master.service_rate_table srt  ' \
                                           'inner join master.service_rates sr on sr.id = srt.service_rate_id ' \
                                           'inner join master.service_masters sm on sm.record_id = sr.service_master_record_id ' \
                                           'inner join transactional.station_services ss on ss.custom_service_rate_record_id = sr.record_id ' \
                                           'inner join transactional.stations s on s.record_id = ss.station_record_id ' \
                                           'where s.record_id = \'%s\' ' \
                                           'and sm.parameters -> \'charging_type\' = \'%s\' ' \
                                           'and srt.validity_start <= \'%s\' and srt.validity_end >= \'%s\' ' \
                                           'and ' \
                                           'srt.days_of_week = ( ' \
                                           'select min(srt.days_of_week) ' \
                                           'from master.service_rate_table srt ' \
                                           'inner join master.service_rates sr on sr.id = srt.service_rate_id ' \
                                           'inner join master.service_masters sm on sm.record_id = sr.service_master_record_id ' \
                                           'inner join transactional.station_services ss on ss.custom_service_rate_record_id = sr.record_id ' \
                                           'where ss.station_record_id = \'%s\' ' \
                                           'and sm.type = \'%s\' ' \
                                           'and srt.validity_start <= \'%s\' and srt.validity_end >= \'%s\' ' \
                                           'and( srt.days_of_week & cast (power(2,extract(isodow from \'%s\'::date)) as bigint) = cast (power(2,extract(isodow from \'%s\'::date)) as bigint)) ' \
                                           ') ' \
                                           'order by sm.name, segment_of_day;'

TOTAL_DURATION_QUERY_FOR_EACH_STATION_BY_DATE = 'with output as ( ' \
                                                'select b.service_date as date, ' \
                                                'extract(hour from sum(s.end_time - s.start_time)) as charging_hours, ' \
                                                'extract(minute from sum(s.end_time - s.start_time)) as charging_minutes, ' \
                                                'extract(epoch from sum(s.end_time - s.start_time)) as charging_time_in_sec ' \
                                                'from transactional.bookings b ' \
                                                'inner join transactional.slots s ' \
                                                'on s.id = b.slot_id ' \
                                                'where b.station_record_id = \'%s\' ' \
                                                'and b.booking_status in (\'FULFILLED\', \'BOOKED\')' \
                                                'and b.service_date between \'%s\' and \'%s\' ' \
                                                'group by b.service_date ' \
                                                'order by b.service_date desc ' \
                                                ') ' \
                                                'select def.default_date as date, ' \
                                                'coalesce(o.charging_hours, 0) as charging_hours, ' \
                                                'coalesce(o.charging_minutes, 0) as charging_minutes, ' \
                                                'coalesce(o.charging_time_in_sec, 0) as charging_time_in_sec ' \
                                                'from ( ' \
                                                '	select \'%s\'::date as default_date ' \
                                                '	union all ' \
                                                '	select \'%s\'::date as default_date ' \
                                                ') def ' \
                                                'left outer join output o ' \
                                                'on o.date = def.default_date;'

BOOKING_COUNT_FOR_EACH_STATION_BY_DATE = 'with output as (select service_date as date, count(1) as booking_count ' \
                                         'from transactional.bookings  ' \
                                         'where station_record_id = \'%s\' ' \
                                         'and booking_status in (\'BOOKED\', \'FULFILLED\', \'MISSED\') ' \
                                         'and service_date between \'%s\' and \'%s\'  ' \
                                         'group by service_date ' \
                                         'order by service_date desc ' \
                                         ') ' \
                                         'select def.default_date as date, ' \
                                         'coalesce(o.booking_count,0) as booking_count ' \
                                         'from ( ' \
                                         'select \'%s\'::date as default_date ' \
                                         'union all ' \
                                         'select \'%s\'::date as default_date ' \
                                         ') def ' \
                                         'left outer join output o ' \
                                         'on o.date = def.default_date;'

ENERGY_CONSUMED_FOR_EACH_STATION_BY_DATE = 'with output as ( ' \
                                           'select ec.reading_date as date,  ' \
                                           '(sum(ec.grid_power)/4 + sum(ec.diesel_generated_power)/4 + ' \
                                           'sum(ec.solar_power)/4) as total_power ' \
                                           'from telemetry.energy_consumption ec ' \
                                           'inner join telemetry.station_mapping st ' \
                                           'on st.station_client_code = ec.station_client_code ' \
                                           'inner join transactional.stations s on s.record_id = st.station_record_id ' \
                                           'where s.record_id = \'%s\' ' \
                                           'and ec.reading_date between \'%s\' and \'%s\' ' \
                                           'group by ec.reading_date ' \
                                           'order by ec.reading_date desc ' \
                                           ') ' \
                                           'select def.default_date as date,  ' \
                                           'coalesce(o.total_power, 0) as total_power ' \
                                           'from ( ' \
                                           ' select \'%s\'::date as default_date ' \
                                           ' union all ' \
                                           ' select \'%s\'::date as default_date ' \
                                           ') def ' \
                                           'left outer join output o ' \
                                           'on o.date = def.default_date;'

OUTAGES_FOR_EACH_STATION_BY_DATE = 'select count(1), \'%s\' as date  from transactional.chargers ch ' \
                                   'where ch.station_record_id = \'%s\' ' \
                                   'and ch.status in (\'UNDER_MAINTENANCE\', \'NON_FUNCTIONAL\') ' \
                                   'and (ch.validity_start::timestamp::date <= \'%s\' ' \
                                   ' and ch.validity_end::timestamp::date >= \'%s\') ' \
                                   'union all ' \
                                   'select count(1), \'%s\' as date  from transactional.chargers ch ' \
                                   'where ch.station_record_id = \'%s\' ' \
                                   'and ch.status in (\'UNDER_MAINTENANCE\', \'NON_FUNCTIONAL\') ' \
                                   'and (ch.validity_start::timestamp::date <= \'%s\'  ' \
                                   ' and ch.validity_end::timestamp::date >= \'%s\');'

SOLAR = 'Solar'
SOLAR_KEY = 'Solar'
GRID = 'Grid'
GRID_KEY = 'Grid'
DG = 'DG'
DG_KEY = 'DG'
SOLAR_COLOR_HEX = '#ffb600'
GRID_COLOR_HEX = '#115e67'
DG_COLOR_HEX = '#fc4c02'
KILO_WATT_HOUR = 'kwh'
OUTAGES_GRAPH_TITLE = 'Outages'
OUTAGES_KEY = 'outages-graph'
CHARGING_WISE_CONSUMPTION_TITLE = 'CHARGER WISE ENERGY CONSUMPTION'
CHARGER_WISE_CONSUMPTION_KEY = 'charger-wise-consumption'
REVENUE_TITLE = 'REVENUE'
REVENUE_KEY = 'revenue-graph'
STATION_OUTAGES_API_URL = 'api/v1/reports/station-outages-graph?date=%s&offset=0&limit=31'
STATION_CHARGER_WISE_GRAPH_API_URL = 'api/v1/reports/station-charger-wise-consumption?date=%s&offset=0&limit=31'
STATION_REVENUE_GRAPH_API_URL = 'api/v1/reports/station-revenue?date=%s&offset=0&limit=31'
DAY_KEY = 'DAY'
MONTH_KEY = 'MONTH'

GET_MAX_DATE_FROM_MONTH = 'select max(reading_date) from telemetry.energy_consumption where ' \
                          'extract(month from reading_date) = %s'
DATE_FROM = 'date-from'
DATE_TILL = 'date-till'

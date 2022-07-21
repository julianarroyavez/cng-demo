import enum
import re
import uuid
from app import log
from app.constant import slot_constant
from app.database import db_session
from app.dto.rating.ratings_dto import StationAnalyticsKPI
from app.dto.report.report_model_base import model_to_dict
from app.errors import FileNotExistsError, InvalidParameterError, MissingFieldError, FieldErrors, InvalidFieldError
from app.repository.rating.station_statistics_repository import StationStatisticsRepository
from app.repository.service_rates_repository import ServiceRatesRepository
from app.repository.station_assignment_repository import StationAssignmentRepository
from app.repository.station_medias_repository import StationMediasRepository
from app.repository.station_operation_details_repository import StationOperationDetailsRepository
from app.repository.station_services_repository import StationServicesRepository
from app.repository.stations_repository import StationsRepository
from app.repository.verifications_repository import VerificationsRepository
from app.util import image_util, string_util
from app.util.datetime_util import *
from app.domain.resource_schema import ChargeTypes, Nozzles, RatedPowers

LOG = log.get_logger()

station_url = "/api/v1/stations/"


class StationService:
    class Links(enum.Enum):
        StationId = "/api/v1/stations/{station_id}"
        StationImages = "/api/v1/stations/{station_id}/images/{image_id}"

        def href(self, station_id, image_id):
            return self.value.format(**dict(station_id=station_id, image_id=image_id))

    def validate_evso_registration_request(self, req_body, thumbnail_file, req_auth_claims):

        if 'name' not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.Name)])

        name = req_body['name'].replace(' ', '')
        if not string_util.check_if_alphanumeric(name):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Name)])

        if ('contact' not in req_body) or ('phoneNumber' not in req_body['contact']):
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.PhoneNumber)])

        if not string_util.check_if_alphanumeric(req_body['contact']['phoneNumber']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PhoneNumber)])

        if ('location' not in req_body) or ('pinCode' not in req_body['location']):
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.PinCode)])

        if not string_util.check_if_alphanumeric(req_body['location']['pinCode']):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.PinCode)])

        if 'hasHyggeBox' not in req_body:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.StationRegistrationHyggeBox)])

        if ('operationDetails' not in req_body) or ('operationStart' not in req_body['operationDetails']) or \
                ('operationEnd' not in req_body['operationDetails']):
            raise InvalidParameterError(
                field_errors=[MissingFieldError(FieldErrors.StationRegistrationOperationDetails)])

        if not thumbnail_file:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.StationRegistrationImage)])

    def evso_registration(self, req_body, thumbnail_file, file1, file2, file3, file4, req_auth_claims):
        images = []

        self.validate_evso_registration_request(req_body=req_body, thumbnail_file=thumbnail_file,
                                                req_auth_claims=req_auth_claims)

        LOG.info('validated evso registration request')
        station_name = req_body['name']

        latitude = req_body['location']['latitude']
        longitude = req_body['location']['longitude']
        address = req_body['location']['address']
        pin_code = req_body['location']['pinCode']

        country_code = req_body['contact']['options']['countryCode']

        email = req_body['contact']['email']
        phone_number = req_body['contact']['phoneNumber']
        website = req_body['contact']['website']

        has_hygge_box = req_body['hasHyggeBox']
        services = req_body['services']

        operating_days = 127
        start_time = req_body['operationDetails']['operationStart']
        end_time = req_body['operationDetails']['operationEnd']

        station_code = str(uuid.uuid4())

        with db_session.atomic():
            stations_repository = StationsRepository()
            stations_repository.insert(station_code=station_code,
                                       req_auth_claims=req_auth_claims,
                                       name=station_name,
                                       location_latitude=latitude,
                                       location_longitude=longitude,
                                       address=address,
                                       pin_code=pin_code,
                                       contact_number=phone_number,
                                       website=website,
                                       verified=False,
                                       has_hygge_box=has_hygge_box)

            station_assignment_repository = StationAssignmentRepository()
            station_assignment_repository.insert(station_record_id=station_code,
                                                 req_auth_claims=req_auth_claims,
                                                 verified=False)

            station_operation_details_repository = StationOperationDetailsRepository()
            station_operation_details_repository.insert(station_record_id=station_code,
                                                        req_auth_claims=req_auth_claims,
                                                        operating_days=operating_days,
                                                        operation_start_time=to_time(start_time['time']),
                                                        operation_end_time=to_time(end_time['time']))

            station_statistics_repository = StationStatisticsRepository()
            station_statistics_repository.insert(station_id=station_code,
                                                 average_rating=0.0,
                                                 rating_count=0,
                                                 user_id=req_auth_claims.get('user'),
                                                 now=datetime_now(),
                                                 min_rating=1,
                                                 max_rating=5
                                                 )

            verifications_repository = VerificationsRepository()
            verifications_repository.insert(registered_by=req_auth_claims.get('user'), station_id=station_code)

            for i in services:
                service_id = list(i.values())[0]

                service_rates_repository = ServiceRatesRepository()
                service_rates = service_rates_repository.fetch_by_service_master_record_id(
                    service_master_record_id=service_id, now=datetime_now())

                station_services_repository = StationServicesRepository()
                station_services_repository.insert(station_record_id=station_code,
                                                   req_auth_claims=req_auth_claims,
                                                   service_master_record=service_id,
                                                   custom_service_rate_record_id=service_rates.id)

            station_medias_repository = StationMediasRepository()
            thumbnail = station_medias_repository.insert(station_record_id=station_code,
                                                         req_auth_claims=req_auth_claims,
                                                         image=thumbnail_file.read(),
                                                         image_rank=1)

            if file1 is not None:
                image1 = station_medias_repository.insert(station_record_id=station_code,
                                                          req_auth_claims=req_auth_claims,
                                                          image=file1.file.read(),
                                                          image_rank=2)
                images.append({
                    "id": image1.id,
                    "href": self.Links.StationImages.href(station_id=station_code, image_id=image1.id)})

            if file2 is not None:
                image2 = station_medias_repository.insert(station_record_id=station_code,
                                                          req_auth_claims=req_auth_claims,
                                                          image=file2.file.read(),
                                                          image_rank=3)
                images.append({
                    "id": image2.id,
                    "href": self.Links.StationImages.href(station_id=station_code, image_id=image2.id)})

            if file3 is not None:
                image3 = station_medias_repository.insert(station_record_id=station_code,
                                                          req_auth_claims=req_auth_claims,
                                                          image=file3.file.read(),
                                                          image_rank=4)
                images.append({
                    "id": image3.id,
                    "href": self.Links.StationImages.href(station_id=station_code, image_id=image3.id)})

            if file4 is not None:
                image4 = station_medias_repository.insert(station_record_id=station_code,
                                                          image=file4.file.read(),
                                                          req_auth_claims=req_auth_claims,
                                                          image_rank=5)
                images.append({
                    "id": image4.id,
                    "href": self.Links.StationImages.href(station_id=station_code, image_id=image4.id)})

        return {
            "id": station_code,
            "name": station_name,
            "stationCode": station_code,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
                "pinCode": pin_code
            },
            "contact": {
                "phoneNumber": phone_number,
                "options": {
                    "countryCode": country_code
                },
                "email": email,
                "website": website
            },
            "thumbnail": {
                "id": thumbnail.id,
                "href": self.Links.StationImages.href(station_id=station_code, image_id=thumbnail.id)
            },
            "images": images,
            "hasHyggeBox": has_hygge_box,
            "services": services,
            "_links": {
                "self": {
                    "href": self.Links.StationId.href(station_id=station_code, image_id=None)
                }
            }
        }

    def get_station_image(self, station_id, image_id, size=None):
        station_repository = StationsRepository()
        try:
            image = station_repository.fetch_image_by_id_and_station_id(station_id=station_id, image_id=image_id)
        except Exception:
            raise FileNotExistsError(description="data not found")
        if image is None:
            raise FileNotExistsError(description="data not found")

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

    def get_nearby_stations(self, params):
        # todo handling of param slot-date
        stations_repository = StationsRepository()
        now = datetime_now()

        lat = float(params['nearby'].split(',')[0])
        lon = float(params['nearby'].split(',')[1])

        LOG.info('Params, Latitude, longitude: %s %s %s' % (params, lat, lon))

        stations_list = {}
        try:
            within_range = float(re.findall(r"[-+]?\d*\.\d+|\d+", params['range'])[0])

        except Exception:
            within_range = 2.5  # todo get this value from app_configs

        where_clauses = [True]

        if 'connector-type' in params:
            connectors = [int(x) for x in params['connector-type'].split(',')]
            # for connector in connectors:
            where_clauses.append(Nozzles.charging_connector_record.in_(connectors))
        if 'charging-type' in params:
            where_clauses.append(RatedPowers.charge_type == ChargeTypes(params['charging-type'].upper()))

        stations = stations_repository.fetch_nearby_stations(lat=lat, lon=lon, radius=within_range, unit='K', now=now,
                                                             where_clauses=where_clauses)
        include_params = params['_include'].split(',')
        LOG.info('include params %s' % include_params)
        for station in stations:
            station_ = {
                'id': station.record_id,
                'name': station.name,
                'stationCode': station.station_code,
                '_links': {
                    "navigate": {
                        "href": station_url + str(station.record_id) + "/navigate"
                    }
                },
                'connectorTypes': [],
                'chargingTypes': [],
                'images': []
            }
            stations_list[station.record_id] = station_
            if 'distance' in include_params:
                stations_list[station.record_id]['distance'] = {'fromLocation': {
                    'longitude': lon, 'latitude': lat
                },
                    'value': float(round(station.distance, 1)),
                    'unit': "KM"
                }
            if 'location' in include_params:
                stations_list[station.record_id]['location'] = {
                    'address': station.address,
                    'latitude': float(station.location_latitude),
                    'longitude': float(station.location_longitude),
                    'pinCode': station.pinCode
                }
            if 'slot-count' in include_params:
                stations_list[station.record_id]['slotData'] = self.get_slot_count_for_station(
                    station_id=station.record_id, slot_date=params['slot-date'] if 'slot-date' in params else None
                )
                # {
                #     "availableSlotCount": 5,
                #     "unavailableSlotCount": 2
                # }
            if 'contact' in include_params:
                stations_list[station.record_id]['contact'] = {
                    "phoneNumber": station.contact_number,
                    "options": {
                        "countryCode": '+91'
                    },
                    "email": '',
                    "website": station.website
                }
            if 'analytics' in include_params:
                analytics = [model_to_dict(StationAnalyticsKPI(key='averageRating',
                                                               value=station.station_stat.average_rating_value,
                                                               rank=1)),
                             model_to_dict(StationAnalyticsKPI(key='totalReviews',
                                                               value=f'{station.station_stat.rating_count} Reviews',
                                                               rank=2))]
                stations_list[station.record_id]['analytics'] = analytics

        stations_list = self.set_station_media_and_connector_type_values(include_params=include_params,
                                                                         stations_list=stations_list)
        response_stations_list = list(stations_list.values())
        response_stations_list = self.set_charging_type_for_station_values(
            include_params=include_params,
            stations_list=stations_list,
            response_stations_list=response_stations_list)
        return {
            "stations": response_stations_list
        }

    def embed_stations(self, root_body, user_id, params):
        station_to_embed = []
        station_assignment_repository = StationAssignmentRepository()
        station_repository = StationsRepository()
        station_medias_repository = StationMediasRepository()

        station_assignments = station_assignment_repository.fetch_all_by_user_record_id(now=datetime_now(),
                                                                                        user_id=user_id)

        for station_assignment in station_assignments:
            thumbnail = station_medias_repository.fetch_by_station_id(station_id=station_assignment.station_record_id,
                                                                      rank=1)
            stations = station_repository.fetch_by_record_id(now=datetime_now(),
                                                             station_id=station_assignment.station_record_id)
            for station in stations:
                station_to_embed.append({
                    "name": station.name,
                    'id': station.record_id,
                    "location": {
                        "latitude": station.location_latitude,
                        "longitude": station.location_longitude,
                        "address": station.address,
                        "pinCode": station.pinCode
                    },
                    "contact": {
                        "phoneNumber": station.contact_number,
                        "website": station.website
                    },
                    "thumbnail": {
                        "href": self.Links.StationImages.href(station_id=station.record_id, image_id=thumbnail.id)
                    },
                    'verified': station.verified
                })

        stations = {
            'stations': station_to_embed
        }
        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['stations'] = stations.pop('stations')

    def set_station_media_and_connector_type_values(self, include_params, stations_list):
        stations_repository = StationsRepository()

        station_thumbnail_map = stations_repository.fetch_for_thumbnails(list(stations_list))
        for mapping in station_thumbnail_map:
            stations_list[mapping.station_record]['thumbnail'] = {
                "id": mapping.id,
                "href": station_url + str(mapping.station_record) + "/images/" + str(mapping.id)
            }

        if 'connector-type' in include_params:
            station_connector_map = stations_repository.fetch_for_charging_connectors(station_list=list(stations_list),
                                                                                      now=datetime_now())
            for mapping in station_connector_map:
                stations_list[mapping.record_id]['connectorTypes'].append(
                    {
                        "id": mapping.chargers.nozzles.charging_connector_record
                    }
                )

        if 'image' in include_params:
            station_media_map = stations_repository.fetch_for_media(list(stations_list))

            for mapping in station_media_map:
                stations_list[mapping.record_id]['images'].append(
                    {
                        "id": mapping.media.id,
                        "href": station_url + str(mapping.record_id) + "/images/" + str(mapping.media.id),
                        "rank": mapping.media.image_rank
                    }
                )
        return stations_list

    def set_charging_type_for_station_values(self, include_params, stations_list, response_stations_list):
        stations_repository = StationsRepository()
        if 'charging-type' in include_params:
            station_rated_power_map = stations_repository.fetch_for_rated_powers(station_list=list(stations_list),
                                                                                 now=datetime_now())

            for mapping in station_rated_power_map:
                stations_list[mapping.record_id]['chargingTypes'].append(
                    {
                        "id": mapping.chargers.nozzles.rated_powers.record_id,
                        "chargingType": mapping.chargers.nozzles.rated_powers.charge_type.value
                    }
                )

            for station in response_stations_list:
                charging_types = set([])
                charging_id_type_map = {}
                for charging_type in station['chargingTypes']:
                    charging_types.add(charging_type['id'])
                    charging_id_type_map[charging_type['id']] = charging_type['chargingType']

                station['chargingTypes'] = []
                for charging_type in charging_types:
                    station['chargingTypes'].append({
                        "id": charging_type,
                        "chargingType": charging_id_type_map[charging_type]
                    })
        return response_stations_list

    @staticmethod
    def get_slot_count_for_station(station_id, slot_date=None):
        ist_time = datetime.datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))  # todo from station
        query_time = str(ist_time.strftime(time_format_in_hh_mm_ss))
        current_date = str(ist_time.date())
        if slot_date is not None and current_date != slot_date:
            query_time = "00:00:01"

        slot_cursor = db_session.execute_sql(
            slot_constant.slot_count_for_station % (
                query_time,
                query_time,
                station_id))

        query_date = slot_date if slot_date is not None else current_date
        booking_cursor = db_session.execute_sql(
            slot_constant.booking_count_for_available_slots % (
                station_id,
                query_date,
                query_time))

        slot = slot_cursor.fetchone()

        booking_count = booking_cursor.fetchone()[0]

        total_slots = slot[0] * 2  # todo I am multiply by 2 cause in this first cng release slots are 30 min.
        available_slots = slot[1] * 2
        if total_slots < available_slots:
            available_slots = 0
        if total_slots == available_slots:
            unavailable_slots = 0
        else:
            # unavailable_slots = total_slots - (available_slots + (float(booking_count[0])))
            unavailable_slots = total_slots - (available_slots - booking_count)
        if available_slots < 0:
            available_slots = 0
        LOG.info(f'{total_slots}, {available_slots}, {unavailable_slots}')
        return {
            "availableSlotCount": int(available_slots),
            "unavailableSlotCount": int(unavailable_slots)
        }

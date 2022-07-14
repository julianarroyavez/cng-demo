class BookingDto:

    def __init__(self, booking_data, connector_type, license_number, included_params=None, qr_code=None,
                 context=None, charging_services=None, value_add_services=None, include_params=None):
        self.booking_id = str(booking_data.booking_id)
        self.service_date = str(booking_data.service_date)
        self.status = str(booking_data.booking_status.value)
        self.slot_time = included_params['slot_time']
        self.slot_number = included_params['slot']['slotNumber']
        self.connector_type = connector_type
        self.license_number = license_number

        if include_params:
            if 'qr_code' in include_params:
                self.qr_code = qr_code
            if 'slot' in include_params:
                self.slot = included_params['slot']
            if 'charging_services' in include_params:
                self.charging_services = charging_services
            if 'value_add_services' in include_params:
                self.value_add_services = value_add_services
            if 'station' in include_params:
                self.station = included_params['station']
            if 'vehicle' in include_params:
                self.vehicle = included_params['vehicle']
            if 'payment' in include_params:
                self.payment = included_params['payment']
            if 'service_otp' in include_params:
                self.service_otp = str(booking_data.otp)
            if 'context' in include_params:
                self.context = context
            if 'status_description' in include_params:
                self.status_desc = str(booking_data.booking_status.value)


class QrCode:

    def __init__(self, data) -> None:
        self.data = data


class SlotDto:

    def __init__(self, name, start_time, end_time, slot_number) -> None:
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.slot_number = slot_number


class ChargingServices:

    def __init__(self, name, charging_id, charging_type, icon_image, rated_power, rates) -> None:
        self.name = name
        self.id = charging_id
        self.type = charging_type
        self.icon_image = icon_image
        self.rated_power = rated_power
        self.rates = rates


class ValueAddServices:

    def __init__(self, name, service_id, service_type, icon_image, rated_power, rates) -> None:
        self.name = name
        self.id = service_id
        self.type = service_type
        self.icon_image = icon_image
        self.rated_power = rated_power
        self.rates = rates


class StationDto:

    def __init__(self, name, latitude, longitude, code) -> None:
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.code = code


class EvsoBookingsDto:

    def __init__(self, vehicle_registration_number, vehicle_connector_type, slot_time, total_charge, booking_status):
        self.car_license = vehicle_registration_number
        self.connector_type = vehicle_connector_type
        self.time_slot = slot_time
        self.total_charge = total_charge
        self.status = booking_status


class TotalAmount:

    def __init__(self, value, currency):
        self.value = value
        self.currency = currency


class PaymentDto:

    def __init__(self, total_amount):
        self.total_amount = total_amount


class ModelImage:

    def __init__(self, href):
        self.href = href


class VehicleMasterDto:

    def __init__(self, id, model, maker, year, image, is_image_allowed=False):
        self.id = id
        self.model = model
        self.maker = maker
        self.year = year
        if is_image_allowed:
            self.model_image = image


class RegistrationCertificate:

    def __init__(self, image):
        self.href = image


class VehicleDto:

    def __init__(self, vehicle_id, reg_number, vehicle_master, registration_certificate, is_image_allowed=False):
        self.id = vehicle_id
        self.car_license = reg_number
        self.vehicle_master = vehicle_master
        if is_image_allowed:
            self.registration_certificate = registration_certificate


class BookingResponseEVSO:

    def __init__(self, bookings: list = None, date_range: str = None) -> None:
        self.bookings = bookings
        self.date_range = date_range

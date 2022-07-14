from peewee import fn

from app.domain.resource_schema import Vehicles, VehicleMasters


class VehiclesRepository:
    def fetch_all_by_user(self, columns, user_id, now):
        return (Vehicles
                .select(*columns)
                .join(VehicleMasters)
                .where((Vehicles.user_record_id == user_id)
                       & (Vehicles.validity_start <= now)
                       & (Vehicles.validity_end > now)))

    def fetch_by_record_id(self, record_id, now):
        return (Vehicles
                .select()
                .where((Vehicles.record_id == record_id)
                       & (Vehicles.validity_start <= now)
                       & (Vehicles.validity_end > now))
                .get())

    def fetch_by_id(self, columns, record_id, now):
        return (Vehicles
                .select(*columns)
                .join(VehicleMasters)
                .where((Vehicles.record_id == record_id)
                       & (Vehicles.validity_start <= now)
                       & (Vehicles.validity_end > now))
                .get())

    def fetch_rc_image_by_vehicles_id(self, vehicle_id, now):
        return (Vehicles
                .select(Vehicles.registration_certificate_image)
                .where((Vehicles.record_id == vehicle_id)
                       & (Vehicles.validity_start <= now)
                       & (Vehicles.validity_end > now))
                .get()
                .registration_certificate_image)

    def validate_by_registration_number(self, registration_number):
        query = (Vehicles
                 .select()
                 .where(fn.Lower(Vehicles.registration_number) == registration_number.lower()))
        return query.exists()

    def insert(self, primary_key, user_id, registration_number, registration_certificate_image, vehicle_master_id):
        return Vehicles.create(
            id=primary_key,
            record_id=primary_key,
            created_by=user_id,
            modified_by=user_id,
            registration_number=registration_number,
            registration_certificate_image=registration_certificate_image,
            vehicle_master_id=vehicle_master_id,
            user_record_id=user_id
        )

    def update_verified_state(self, vehicle, verified):
        vehicle.verified = verified
        vehicle.save()

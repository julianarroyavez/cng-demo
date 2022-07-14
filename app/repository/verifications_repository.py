import datetime

from app.domain.resource_schema import Verifications, VerificationStatus


class VerificationsRepository:
    def insert(self, registered_by=None, user_id=None, vehicle_id=None, station_id=None, verification_expiry=None):
        return (Verifications.create(
            registered_by=registered_by,
            created_by='000000ad-ac99-44c8-9a6b-ca1214a60000',
            modified_by='000000ad-ac99-44c8-9a6b-ca1214a60000',
            registered_user_record_id=user_id,
            registered_vehicle_record_id=vehicle_id,
            registered_station_record_id=station_id,
            verification_status=VerificationStatus.Pending,
            verification_expiry=verification_expiry
        ))

    def fetch_by_user_record_id(self, user_record_id):
        return (Verifications
                .select()
                .where((Verifications.registered_user_record_id == user_record_id))
                .get())

    def fetch_by_vehicle_record_id(self, vehicle_record_id):
        return (Verifications
                .select()
                .where((Verifications.registered_vehicle_record_id == vehicle_record_id))
                .get())

    def update_users_records(self, user_record_id, verifier_id, status, now, verifier_remark):
        return (Verifications
                .update({Verifications.modified_on: now,
                         Verifications.verified_by: verifier_id,
                         Verifications.verification_status: status,
                         Verifications.verification_time: now,
                         Verifications.verifier_remark: verifier_remark,
                         Verifications.verification_expiry: datetime.datetime.max})
                .where((Verifications.registered_user_record_id == user_record_id))
                .execute())

    def update_vehicles_records(self, now, verifier_id, status, verifier_remark, vehicle_record_id):
        return (Verifications
                .update({Verifications.modified_on: now,
                         Verifications.verified_by: verifier_id,
                         Verifications.verification_status: status,
                         Verifications.verification_time: now,
                         Verifications.verifier_remark: verifier_remark,
                         Verifications.verification_expiry: datetime.datetime.max})
                .where((Verifications.registered_vehicle_record_id == vehicle_record_id))
                .execute())

    def fetch_by_station_record_id(self, station_record_id):
        return (Verifications
                .select()
                .where((Verifications.registered_station == station_record_id))
                .get())

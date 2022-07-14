from peewee import fn

from app.domain.auth_schema import MobileDevices, EquipmentStatus, EquipmentTypes, Users


class MobileDevicesRepository:

    def insert(self, user, os_name, product_id, model_id, device_token, os_version, brand, app_version, fcm_token,
               record_id, now, device_id):
        if device_id is None:
            device_id = fn.nextval('equipments_id_seq')
        return (MobileDevices
                .create(created_by=user,
                        modified_by=user,
                        id= device_id,
                        record_id=record_id,
                        type=EquipmentTypes.MobileDevice,
                        status=EquipmentStatus.Active,
                        product_id=product_id,
                        model_id=model_id,
                        asset_id=device_token,
                        device_token=device_token,
                        os=os_name,
                        os_version=os_version,
                        brand=brand,
                        app_version=app_version,
                        fcm_token=fcm_token,
                        validity_start=now))

    def fetch_by_device_token(self, device_token, now):
        return (MobileDevices
                .select()
                .where((MobileDevices.device_token == device_token)
                       & (MobileDevices.validity_start <= now)
                       & (MobileDevices.validity_end > now))
                .get())

    def update(self, user, product_id, model_id, os_name, os_version, brand, app_version, fcm_token, record_id, now):
        query = (MobileDevices
                 .update({MobileDevices.modified_on: now,
                          MobileDevices.modified_by: user,
                          MobileDevices.product_id: product_id,
                          MobileDevices.model_id: model_id,
                          MobileDevices.os: os_name,
                          MobileDevices.os_version: os_version,
                          MobileDevices.brand: brand,
                          MobileDevices.app_version: app_version,
                          MobileDevices.fcm_token: fcm_token})
                 .where(MobileDevices.id == record_id))
        return query.execute()

    def update_temporal_record(self, record, user, record_id, now):
        query = (MobileDevices
                 .update({MobileDevices.modified_on: now,
                          MobileDevices.modified_by: user,
                          MobileDevices.validity_end: now})
                 .where(MobileDevices.id == record_id))
        return query.execute()

    def fetch_by_modified_by(self, user_id):
        return (MobileDevices
                .select().distinct()
                .where(MobileDevices.modified_by == user_id)
                .order_by(MobileDevices.modified_on.desc())
                .get())

    def fetch_by_user_phone_number(self, phone_number):
        return (MobileDevices
                .select().distinct()
                .join_from(MobileDevices, Users, attr='modified_by', on=(MobileDevices.modified_by == Users.record_id))
                .where(Users.phone_number == phone_number)
                .order_by(MobileDevices.modified_on.desc())
                .get())

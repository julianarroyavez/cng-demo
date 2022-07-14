from app.domain.resource_schema import EquipmentTypeMasters


class EquipmentTypeMasterRepository:
    def fetch_all(self, now):
        return (EquipmentTypeMasters
                .select()
                .where((EquipmentTypeMasters.validity_end > now)
                       & (EquipmentTypeMasters.validity_start <= now)))

    def fetch_icon_image_by_id(self, record_id, now):
        return (EquipmentTypeMasters
                .select(EquipmentTypeMasters.icon_image)
                .where((EquipmentTypeMasters.record_id == record_id)
                       & (EquipmentTypeMasters.validity_start <= now)
                       & (EquipmentTypeMasters.validity_end > now))
                .get()
                .icon_image)

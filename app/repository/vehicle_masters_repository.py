from app.domain.resource_schema import VehicleMasters


class VehicleMastersRepository:
    def fetch_all(self, columns, now):
        return VehicleMasters.select(
            *columns
        ).where(
            (VehicleMasters.validity_start <= now)
            & (VehicleMasters.validity_end > now)
        )

    def fetch_by_record_id(self, record_id, now):
        return VehicleMasters.select().where(
            (VehicleMasters.record_id == record_id)
            & (VehicleMasters.validity_start <= now)
            & (VehicleMasters.validity_end > now)
        )

    def fetch_model_image_by_id(self, vehicle_master_id, now):
        return VehicleMasters.select(VehicleMasters.image).where(
            (VehicleMasters.id == vehicle_master_id)
            & (VehicleMasters.validity_start <= now)
            & (VehicleMasters.validity_end > now)
        ).get().image

    def fetch_by_class_name(self, class_name, now):
        return VehicleMasters.select().where(
            (VehicleMasters.class_of_vehicle == class_name)
            & (VehicleMasters.validity_start <= now)
            & (VehicleMasters.validity_end > now)
        )

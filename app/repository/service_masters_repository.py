from app.domain.booking_schema import ServiceMasters


class ServiceMastersRepository:
    def fetch_by_record_id(self, columns, now, record_id):
        return ServiceMasters.select(
            *columns
        ).where(
            (ServiceMasters.validity_start <= now)
            & (ServiceMasters.validity_end > now)
            & (ServiceMasters.record_id == record_id)
        ).get()

    def fetch_by_type(self, now, type_list):
        return ServiceMasters.select().where(
            ServiceMasters.type.in_(type_list)
            & (ServiceMasters.validity_start <= now)
            & (ServiceMasters.validity_end > now)
        )

    def fetch_icon_image_by_id(self, service_id):
        return ServiceMasters.select(ServiceMasters.icon_image).where(
            ServiceMasters.id == service_id
        ).get().icon_image

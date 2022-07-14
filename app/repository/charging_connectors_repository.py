from app.domain.resource_schema import ChargingConnectors


class ChargingConnectorsRepository:

    def fetch_all(self, now=None):
        return ChargingConnectors.select().where((ChargingConnectors.validity_start <= now)
                                                 & (ChargingConnectors.validity_end > now))

    def fetch_icon_image_by_id(self, record_id, now=None):
        return ChargingConnectors.select(ChargingConnectors.icon_image).where(
            (ChargingConnectors.id == record_id)
            & (ChargingConnectors.validity_start <= now)
            & (ChargingConnectors.validity_end > now)
        ).get().icon_image

    def fetch_names_by_ids(self, record_ids, now):
        return ChargingConnectors.select().where(
            (ChargingConnectors.id.in_(record_ids))
            & (ChargingConnectors.validity_start <= now)
            & (ChargingConnectors.validity_end > now))

    def fetch_name_by_id(self, record_id, now):
        return ChargingConnectors.select(ChargingConnectors.name).where(
            (ChargingConnectors.id == record_id)
            & (ChargingConnectors.validity_start <= now)
            & (ChargingConnectors.validity_end > now)
        ).get().name

    def fetch_all_by_ids(self, now=None, ids=None):
        return ChargingConnectors.select().where((ChargingConnectors.id.in_(ids)) &
                                                 (ChargingConnectors.validity_start <= now)
                                                 & (ChargingConnectors.validity_end > now))

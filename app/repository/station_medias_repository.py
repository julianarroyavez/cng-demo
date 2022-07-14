from app.domain.resource_schema import StationMedias


class StationMediasRepository:
    def insert(self, station_record_id, req_auth_claims, image, image_rank):
        return StationMedias.create(station_record=station_record_id,
                                    created_by=req_auth_claims.get('user'),
                                    modified_by=req_auth_claims.get('user'),
                                    image=image,
                                    image_rank=image_rank)

    def fetch_by_station_id(self, station_id, rank):
        return StationMedias.select().where(
            (StationMedias.station_record == station_id)
            & (StationMedias.image_rank == rank)
        ).get()

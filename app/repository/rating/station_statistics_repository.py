from peewee import fn

from app.domain.rating.rating_schema import StationStatistics


class StationStatisticsRepository:

    def insert(self, station_id, average_rating, rating_count, now, user_id,
               min_rating=None, max_rating=None):
        return (StationStatistics.create(
            id=fn.nextval('analytics.station_statistics_id_seq'),
            created_on=now,
            modified_on=now,
            created_by=user_id,
            modified_by=user_id,
            rated_station=station_id,
            average_rating_value=average_rating,
            rating_count=rating_count,
            min_rating=min_rating,
            max_rating=max_rating
        ))

    def update(self, station_id, average_rating, rating_count, now):
        (StationStatistics
         .update({
            StationStatistics.average_rating_value: average_rating,
            StationStatistics.rating_count: rating_count,
            StationStatistics.modified_on: now
        })
         .where(StationStatistics.rated_station == station_id)
         .execute())

    def fetch_by_station_id(self, station_id):
        return (StationStatistics
                .select()
                .where(StationStatistics.rated_station == station_id)
                .get())

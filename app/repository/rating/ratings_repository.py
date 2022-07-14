from peewee import fn, JOIN

from app.database import db_session
from app.domain.rating.rating_schema import Ratings, RatingAttachments
from app.repository.rating.rating_attachments_repository import RatingAttachmentsRepository


class RatingsRepository:

    def insert(self, user_id, rating_value, rating_explanation, now, has_attachments=False,
               attachments=None, station_id=None, booking_id=None):
        with db_session.atomic():
            newly_added_rating = (Ratings.create(
                id=fn.nextval('ratings_id_seq'),
                created_by=user_id,
                modified_by=user_id,
                created_on=now,
                modified_on=now,
                rated_by=user_id,
                rated_station=station_id,
                rated_booking=booking_id,
                rating_value=rating_value,
                rating_explanation=rating_explanation,
                rating_time=now
            ))

            if has_attachments:
                rating_attachments_repository = RatingAttachmentsRepository()
                for attachment in attachments:
                    rating_attachments_repository.insert(
                        rating_id=newly_added_rating.id,
                        attachment=attachment.read(),
                        user_id=user_id,
                        now=now
                    )
            return newly_added_rating

    def fetch_ratings_by_station_id(self, station_id, limit, offset, columns):
        return (Ratings
                .select(*columns)
                .join_from(Ratings, RatingAttachments, on=(Ratings.id == RatingAttachments.rating_id),
                           attr='rating_attachments', join_type=JOIN.LEFT_OUTER)
                .where(Ratings.rated_station == station_id)
                .order_by(Ratings.created_on.desc())
                .limit(limit)
                .offset(offset)
                )

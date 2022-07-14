from peewee import fn

from app.domain.rating.rating_schema import RatingAttachments


class RatingAttachmentsRepository:

    def insert(self, user_id, rating_id, attachment, now):
        return (RatingAttachments.create(
            id=fn.nextval('rating_attachments_id_seq'),
            created_by=user_id,
            modified_by=user_id,
            created_on=now,
            modified_on=now,
            rating_id=rating_id,
            attachment=attachment
        ))
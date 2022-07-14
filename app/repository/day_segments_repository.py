from app.domain.booking_schema import SegmentsOfDay


class DaySegmentsRepository:

    def fetch_all(self):
        return (SegmentsOfDay
                .select().order_by(SegmentsOfDay.segment_end_time))

    def fetch_icon_image_by_id(self, segment_id):
        return (SegmentsOfDay
                .select(SegmentsOfDay.icon_image)
                .where(SegmentsOfDay.id == segment_id)
                .get()
                .icon_image)

    def fetch_by_id(self, segment_id):
        return (SegmentsOfDay.
                select(SegmentsOfDay.id)
                .where(SegmentsOfDay.id == segment_id)
                .get())

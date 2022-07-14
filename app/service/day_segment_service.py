import enum

from app.repository.day_segments_repository import DaySegmentsRepository
from app.util import image_util


class SegmentOfDayService:
    class Links(enum.Enum):
        IconImage = '/api/v1/day-segments/{key}/icon-image'

        def href(self, key):
            return self.value.format(**dict(key=key))

    def embed_segments_of_day(self, root_body, user_id, params):
        segments_of_day = DaySegmentsRepository().fetch_all()

        embed_list = []
        for segment in segments_of_day:
            embed_list.append({
                "id": segment.id,
                "name": segment.name,
                "value": segment.key.value,
                "segmentStartTime": segment.segment_start_time,
                "segmentEndTime": segment.segment_end_time,
                "iconImage": {
                    "href": self.Links.IconImage.href(key=segment.id)
                }
            })

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['daySegments'] = embed_list

    def get_icons_of_segment(self, segment_id, size=None):
        day_segments_repository = DaySegmentsRepository()
        image = day_segments_repository.fetch_icon_image_by_id(segment_id=segment_id)

        return image.tobytes() if size is None else image_util.transform_image(image.tobytes(),
                                                                               tuple(map(int, size.split(","))))

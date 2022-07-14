from app.domain.rating.rating_schema import Ratings, RatingAttachments
from app.dto.rating.ratings_dto import RatingsResponseDto
from app.dto.report.report_model_base import model_to_dict
from app.errors import InvalidParameterError, FieldErrors, InvalidFieldError
from app.log import LOG
from app.repository.rating.ratings_repository import RatingsRepository
from app.repository.rating.station_statistics_repository import StationStatisticsRepository
from app.util import string_util
from app.util.datetime_util import datetime_now
from app.util.rating.ratings_util import RatingsUtil


class RatingsService:

    def save_rating(self, req_body, user_id, object_id, attachment_one=None,
                    attachment_two=None, attachment_three=None, is_station=False):

        ratings_repository = RatingsRepository()
        ratings_util = RatingsUtil()

        text = req_body['ratingExplanation'].replace('\n', '')
        text = text.replace(' ', '')
        if not string_util.check_if_alphanumeric(text):
            raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.Rating)])

        rating_dto = ratings_util.create_rating_object_from_req_body(data=req_body, is_station=is_station,
                                                                     object_id=object_id)

        has_attachments = False
        attachments = []

        if attachment_one:
            has_attachments = True
            attachments.append(attachment_one)
        if attachment_two:
            attachments.append(attachment_two)
        if attachment_three:
            attachments.append(attachment_three)

        ratings_repository.insert(
            user_id=user_id,
            attachments=attachments,
            has_attachments=has_attachments,
            rating_value=rating_dto.rating_value,
            station_id=rating_dto.rated_station,
            booking_id=rating_dto.rated_booking,
            rating_explanation=rating_dto.rating_explanation,
            now=datetime_now()
        )

        if is_station:
            self.update_station_statistics(station_id=rating_dto.rated_station,
                                           newly_added_rating=rating_dto.rating_value,
                                           user_id=user_id)

        return model_to_dict(RatingsResponseDto(message="Your Station rating and feedback is saved",
                                                rating_id=rating_dto.id))

    def update_station_statistics(self, station_id, newly_added_rating, user_id=None):
        station_statistics_repository = StationStatisticsRepository()
        try:
            station_stat = station_statistics_repository.fetch_by_station_id(station_id=station_id)
            new_average_rating = self.__calculate_average_rating__(
                current_rating=station_stat.average_rating_value,
                rating_count=station_stat.rating_count,
                newly_added_rating=newly_added_rating
            )
            station_statistics_repository.update(
                station_id=station_id,
                average_rating=new_average_rating,
                rating_count=station_stat.rating_count + 1,
                now=datetime_now()
            )

        except Exception as e:
            LOG.error('No station statistics data found for station ID: %s... creating new record due to error %s' %
                      (station_id, e))
            try:
                station_stat = station_statistics_repository.insert(
                    station_id=station_id,
                    average_rating=newly_added_rating,
                    rating_count=1,
                    user_id=user_id,
                    now=datetime_now(),
                    min_rating=1,
                    max_rating=5
                )
            except Exception as e:
                LOG.error('Unable to add stats for station with ID %s due to error %s' % (station_id, e))

    def __calculate_average_rating__(self, current_rating, rating_count, newly_added_rating):
        return round(((rating_count * current_rating) + newly_added_rating) / (rating_count + 1), 2)

    def fetch_station_ratings(self, station_id, limit, offset):

        ratings_repository = RatingsRepository()
        columns = [Ratings.id, Ratings.rating_value, Ratings.rating_time, Ratings.rating_explanation,
                   Ratings.rated_station, Ratings.rated_booking,
                   RatingAttachments.attachment]
        ratings_repository.fetch_ratings_by_station_id(station_id=station_id, limit=limit, offset=offset,
                                                       columns=columns)

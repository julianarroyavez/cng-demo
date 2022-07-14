from app.dto.rating.ratings_dto import RatingsDto


class RatingsUtil:

    def create_rating_object_from_req_body(self, data, is_station, object_id):
        if is_station:
            return RatingsDto(rating_value=data['ratingValue'], rating_time=data['ratingTime'],
                              rating_explanation=data['ratingExplanation'], rated_station=object_id,
                              client_id=data['id'])

        return RatingsDto(rating_value=data['ratingValue'], rating_time=data['ratingTime'],
                          rating_explanation=data['ratingExplanation'], rated_booking=object_id, client_id=data['id'])

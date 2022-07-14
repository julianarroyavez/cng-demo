
class RatingsDto:

    def __init__(self, rating_value, rating_explanation, rating_time, rated_station=None, rated_booking=None,
                 client_id=None):
        self.rating_value = rating_value
        self.rating_time = rating_time
        self.rating_explanation = rating_explanation
        self.rated_station = rated_station
        self.rated_booking = rated_booking
        self.id = client_id


class RatingsResponseDto:

    def __init__(self, message, rating_id):
        self.id = rating_id
        self.message = message


class StationAnalyticsKPI:

    def __init__(self, key, value, rank):
        self.key = key
        self.value = value
        self.rank = rank


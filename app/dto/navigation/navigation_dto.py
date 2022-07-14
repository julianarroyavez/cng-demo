
class Coordinate:

    def __init__(self, latitude: str, longitude: str):
        self.latitude = latitude
        self.longitude = longitude


class NavigationDto:

    def __init__(self, origin: Coordinate, destination: Coordinate):
        self.origin = origin
        self.destination = destination

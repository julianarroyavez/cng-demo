from math import radians, cos, sin, asin, sqrt, atan2


def get_distance(current_lat, current_lon, station_lat, station_lon):
    current_lat = radians(current_lat)
    current_lon = radians(current_lon)
    radius = 6371
    difference_lon = radians(station_lon) - current_lon
    difference_lat = radians(station_lat) - current_lat
    # Haversine formula
    answer = sin(difference_lat / 2) ** 2 + cos(current_lat) * cos(station_lat) * sin(difference_lon / 2) ** 2
    c = 2 * asin(sqrt(answer))
    distance = c * radius
    return float(round(distance, 1))

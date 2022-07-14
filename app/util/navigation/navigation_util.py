from app.dto.navigation.navigation_dto import Coordinate, NavigationDto


class NavigationUtil:

    def convert_query_params_to_navigation_object(self, origin, destination):
        origin_coordinates = origin.split(',')
        dest_coordinates = destination.split(',')
        origin_data = Coordinate(latitude=origin_coordinates[0], longitude=origin_coordinates[1])
        destination_data = Coordinate(latitude=dest_coordinates[0], longitude=dest_coordinates[1])

        query_param = NavigationDto(origin=origin_data, destination=destination_data)
        return query_param

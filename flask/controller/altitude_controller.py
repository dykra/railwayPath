from flask import jsonify

from repository.altitude_repository import AltitudeRepository
from static.utils import parse_result_string_to_map


class AltitudeController:
    def __init__(self):
        self.repository = AltitudeRepository()
    def get_altitude_from_database_as_json(self, latitude_str, longitude_str):
        result_map = {"latitude": latitude_str, "longitude": longitude_str}
        result_map["altitude"] = self.repository.get_altitude_from_database(latitude_str, longitude_str)
        return jsonify(result_map)

    def get_altitude_list_from_database_as_json(self, points_string):
        result_string = self.repository.get_altitudes_string_from_database(points_string)
        result_map = parse_result_string_to_map(result_string)
        return str(result_map)

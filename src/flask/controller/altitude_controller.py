from flask import jsonify

from repository.altitude_repository import AltitudeRepository

class AltitudeController:
    def __init__(self):
        self.repository = AltitudeRepository()
    def get_altitude_from_database_as_json(self, latitude_str, longitude_str):
        result_map = {"latitude": latitude_str, "longitude": longitude_str}
        result_map["altitude"] = self.repository.get_altitude_from_database(latitude_str, longitude_str)
        return jsonify(result_map)
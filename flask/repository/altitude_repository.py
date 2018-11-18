from static.utils import get_db_connection


class AltitudeRepository:
    def __init__(self):
        self.db = get_db_connection()

    def get_altitude_from_database(self, latitude_str, longitude_str):
        altitude_cursor = self.db.execute_statement(
        "select dbo.getAltitudeFromCoordinates({}, {})".format(latitude_str, longitude_str))
        return float(altitude_cursor.fetchall()[0][0])

    def get_altitudes_string_from_database(self, points_string):
        command = "select dbo.getAltitudesFromCoordinateList(\'{}\')".format(points_string)
        altitude_cursor = self.db.execute_statement(command)
        return altitude_cursor.fetchall()[0][0]


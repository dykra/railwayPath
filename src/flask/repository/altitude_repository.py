from app import db_connection


class AltitudeRepository:
    def __init__(self):
        self.db = db_connection

    def get_altitude_from_database(self, latitude_str, longitude_str):
        altitude_cursor = self.db.execute_statement(
        "select dbo.getAltitudeFromCoordinates({}, {})".format(latitude_str, longitude_str))
        return float(altitude_cursor.fetchall()[0][0])


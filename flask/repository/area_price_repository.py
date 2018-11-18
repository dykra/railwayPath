from static.utils import get_db_connection


class AreaPriceRepository:
    def __init__(self):
        self.db = get_db_connection()

    def get_price_of_area(self, points_string):
        # TODO uncommennt lines below as soon as the method in the database is implemented
        # area_price_cursor = self.db.execute_statement(
        # "select dbo.getPriceOfThisArea({})".format(points_string))
        # return float(area_price_cursor.fetchall()[0][0])
        return 5.5

from flask import jsonify

from repository.area_price_repository import AreaPriceRepository


class AreaPriceController:
    def __init__(self):
        self.repository = AreaPriceRepository()
    def get_price_of_area_as_json(self, points_string):
        result_map = {}
        result_map["price"] = self.repository.get_price_of_area(points_string)
        return jsonify(result_map)
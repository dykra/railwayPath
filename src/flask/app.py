from flask import Flask, request

from controller.altitude_controller import AltitudeController
from controller.area_price_controller import AreaPriceController
from static.DatabaseHandler import DatabaseHandler
from static.utils import convert_points_list_to_points_string

app = Flask(__name__)

db_connection = DatabaseHandler('89.69.106.183:50002', 'agh', 'agh', 'LosAngelesCounty')

@app.route('/altitude', methods = ['GET'])
def get_altitude():
    latitude_str = request.args.get("latitude")
    longitude_str = request.args.get("longitude")

    altCtrl = AltitudeController()

    return altCtrl.get_altitude_from_database_as_json(latitude_str, longitude_str)

@app.route('/areaprice', methods = ['POST'])
def get_area_price():
    points_list = request.form.get('points_list')
    print(points_list)
    points_string = convert_points_list_to_points_string(points_list)

    apController = AreaPriceController()

    return apController.get_price_of_area_as_json(points_string)

if __name__ == '__main__':
    app.run()

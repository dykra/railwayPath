from flask import Flask, request
import json

from controller.altitude_controller import AltitudeController
from controller.area_price_controller import AreaPriceController
from static.utils import convert_points_list_to_points_string

app = Flask(__name__)

@app.route('/altitude', methods = ['GET'])
def get_altitude():
    latitude_str = request.args.get("latitude")
    longitude_str = request.args.get("longitude")

    altCtrl = AltitudeController()

    return altCtrl.get_altitude_from_database_as_json(latitude_str, longitude_str)


@app.route('/altitudes', methods = ['POST'])
def get_altitudes():
    points_list = request.data.decode("utf-8")

    print(points_list)
    x = json.loads(points_list)
    print(x)
    altCtrl = AltitudeController()

    points_string = convert_points_list_to_points_string(x['points_list'])

    return altCtrl.get_altitude_list_from_database_as_json(points_string)


@app.route('/areaprice', methods = ['POST'])
def get_area_price():
    points_list = request.form.get('points_list')
    print(points_list)
    points_string = convert_points_list_to_points_string(points_list)

    apController = AreaPriceController()

    return apController.get_price_of_area_as_json(points_string)

if __name__ == '__main__':
    app.run()

from flask import Flask, request, jsonify
import json


from controller.altitude_controller import AltitudeController
from controller.area_price_controller import AreaPriceController
from static.utils import convert_points_list_to_points_string, get_db_connection, create_select_for_ids_list
from flask_cors import CORS

class InternalServerError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv



app = Flask(__name__)
CORS(app)
@app.route('/altitude', methods = ['GET'])
def get_altitude():
    try:
        latitude_str = request.args.get("latitude")
        longitude_str = request.args.get("longitude")

        altCtrl = AltitudeController()

        return altCtrl.get_altitude_from_database_as_json(latitude_str, longitude_str)
    except Exception as e:
        raise InternalServerError('Unhandled error on server. Please try again. Message: ' + str(e), status_code=500)


@app.route('/altitudes', methods = ['POST'])
def get_altitudes():
    try:
        points_list = request.data.decode("utf-8")

        print(points_list)
        x = json.loads(points_list)

        altCtrl = AltitudeController()

        points_string = convert_points_list_to_points_string(x['points_list'])

        return altCtrl.get_altitude_list_from_database_as_json(points_string)
    except Exception as e:
        raise InternalServerError('Unhandled error on server. Please try again. Message: ' + str(e), status_code=500)




@app.route('/prices', methods = ['POST'])
def get_area_price():
    try:
        data = request.data.decode("utf-8")

        ids_json = json.loads(data)
        ids_list = ids_json['ids']

        sql = create_select_for_ids_list(ids_list)
        conn = get_db_connection()
        cursor = conn.execute_statement(sql)
        parcels = cursor.fetchall()
        result_list = []
        for p in parcels:
            result_list.append({'objectid': p[0], 'zoning_code': p[1], 'price': p[2]})
        return jsonify(result_list)
    except Exception as e:
        raise InternalServerError('Unhandled error on server. Please try again. Message: ' + str(e), status_code=500)




if __name__ == '__main__':
    app.run()

@app.errorhandler(InternalServerError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
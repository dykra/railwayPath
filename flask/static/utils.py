from static.DatabaseHandler import DatabaseHandler

def get_db_connection():
    return DatabaseHandler()


def convert_points_list_to_points_string(points_list):
    result_string = ""

    for point in points_list:
        result_string += "-1," + str(point["longitude"]) + "," + str(point["latitude"]) + ",;"

    return result_string


def parse_result_string_to_map(result_string):
    result_map = []
    # latitude:34.2,longitude:-118.45,altitude:226.208;latitude:34.3,longitude:-117.95,altitude:1721.53;latitude:34.1,longitude:-118.25,altitude:112.331;
    list_of_points = result_string.split(";")[:-1]
    list_of_string_points = [p.split(",") for p in list_of_points]
    correct_map_list = []
    for point in list_of_string_points:
        element = []
        for property in point:
            split_property = property.split(":")
            element.append({split_property[0]: split_property[1]})
        correct_map_list.append(element)

    result_list = []
    for point in correct_map_list:
        result_list.append({"latitude": point[0]['latitude'], "longitude": point[1]['longitude'], "altitude": point[2]['altitude']})

    result_map = {"points": result_list}
    return result_map

def create_select_for_ids_list(ids_list):
    list_string = "("
    for id in ids_list[:-1]:
        list_string += str(id['objectid']) + ","
    list_string += str(ids_list[len(ids_list) - 1]['objectid']) + ")"
    return "select OBJECTID, simple_code, price from dbo.estimated_prices where OBJECTID IN {}".format(list_string)
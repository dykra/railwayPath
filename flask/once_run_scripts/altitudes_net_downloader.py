import math
import time
from datetime import datetime
from multiprocessing import Process

import requests
import pymssql
import json

from flask.static.utils import get_db_connection

print(datetime.now())
def get_point_list_with_altitudes_from_open_elevation_api(points_list):
    post_data = {"locations" : []}
    for point in points_list:
        post_data["locations"].append({"latitude":point[1][1], "longitude": point[1][0]})

    start = time.time()
    r = requests.post(url=get_base_url(), json=post_data)
    stop = time.time()
    print("TIME: " + str(stop - start))

    # print(r.json())
    json_len = len(r.json()['results'])
    json_arr = r.json()['results']

    for i in range(0,json_len):
        points_list[i].append(json_arr[i]['elevation'])
    return points_list


def create_url(points_list):
    base_url = 'https://elevation-api.io/api/elevation?points='
    base_url += "({},{})".format(points_list[0][1][1], points_list[0][1][0])
    for point in points_list[1:]:
        base_url += "({},{})".format(point[1][1], point[1][0])
    return base_url

def get_point_list_with_altitudes_from_elevation_api_io(points_list):

    url = create_url(points_list)

    r = requests.get(url)

    results_list = r.json()['elevations']
    list_len = len(results_list)
    for i in range(0,list_len):
        points_list[i].append(results_list[i]['elevation'])

    return points_list

def get_base_url():
    return 'https://api.open-elevation.com/api/v1/lookup'



# db = DatabaseHandler('89.69.106.183:50002', 'agh', 'agh', 'LosAngelesCounty')
db = get_db_connection()
west = db.execute_statement("select top 1 center_lon from dbo.PARCEL where CENTER_X != 0 and CENTER_Y != 0 order by CENTER_LON")
wlon = float(west.fetchall()[0][0])

east = db.execute_statement("select top 1 center_lon from dbo.PARCEL where CENTER_X != 0 and CENTER_Y != 0 order by CENTER_LON desc")
elon = float(east.fetchall()[0][0])

south = db.execute_statement("select top 1 center_lat from dbo.PARCEL where CENTER_X != 0 and CENTER_Y != 0 order by center_lat")
slat = float(south.fetchall()[0][0])

north = db.execute_statement("select top 1 center_lat from dbo.PARCEL where CENTER_X != 0 and CENTER_Y != 0 order by center_lat desc")
nlat = float(north.fetchall()[0][0])




# WLon:  -118.94033184
# ELon:  -117.65227498
# SLat:  32.80448004
# NLat:  34.82304024

elon = -117.65227498
wlon = -118.94033184
nlat = 34.82304024
slat = 32.80448004

southNorthMeters = 111111 * (elon - wlon)
eastwestMeters = 111111 * math.cos(math.radians(nlat)) * (nlat - slat)
print(southNorthMeters)
print(eastwestMeters)
netDistanceInMeters = 100
how_many_at_one_call = 50
how_many_in_single_thread = 3700

xSideLength = int((eastwestMeters//netDistanceInMeters)) + 1
ySideLength = (southNorthMeters//netDistanceInMeters) + 1

xCoordsCoefficient = (elon - wlon)/xSideLength
yCoordsCoefficient = (nlat - slat)/ySideLength


def getCoords(x, y):
    we = wlon + x * xCoordsCoefficient
    sn = slat + y * yCoordsCoefficient
    return (we, sn)

allCoords = []

total_number = int(xSideLength * ySideLength)

for i in range (0,total_number):
    x = i % xSideLength
    y = i // xSideLength
    allCoords.append([i,getCoords(x,y)])


def generate_insert_for_point(point):
    return "insert into altitudesNet (number, altitude) values ({}, {});\n".format(point[0],point[2])



def generate_inserts_from_points(all_points_with_numbers_and_altitudes):
    result = ""
    for point in all_points_with_numbers_and_altitudes:
        result += generate_insert_for_point(point)
    return result


def print_points_to_file(text, name):
    text_file = open(name, "w")
    text_file.write(text)
    text_file.close()


def single_altitude_thread(coords, thr_number):
    all_points_with_numbers_and_altitudes = []
    print("insert",thr_number)
    for ind in range(0, len(coords), how_many_at_one_call):
        correct = False
        while (not correct):
            try:
                start = time.time()
                all_points_with_numbers_and_altitudes.extend(
                    # get_point_list_with_altitudes_from_open_elevation_api(coords[ind:ind + how_many_at_one_call]))
                    get_point_list_with_altitudes_from_elevation_api_io(coords[ind:ind + how_many_at_one_call]))
                # print(all_points_with_numbers_and_altitudes)
                stop = time.time()
                print("TOTAL TIME: " + str(stop - start))
                correct = True
            except:
                correct = False
        print(thr_number, ind)
    name = "yinsert" + str(thr_number) + ".txt"
    print_points_to_file(generate_inserts_from_points(all_points_with_numbers_and_altitudes), name)

# single_altitude_thread(allCoords[:5000], "3")


processes = []

print("South: ", slat)
print("North: ", nlat)
print("East: ", elon)
print("West: ", wlon)
print("XCoordsStep: ", xCoordsCoefficient)
print("YCoordsStep: ", yCoordsCoefficient)
print("XSideLength: ", xSideLength)
print("YSideLength: ", ySideLength)
conf_str = "{netsize: {}, south: {}, north: {}, east: {}, west: {}, xcoordsstep: {}, ycoordsstep: {}, xsidelength: {}, ysidelength: {}}".format(netDistanceInMeters, slat, nlat, elon, wlon, xCoordsCoefficient, yCoordsCoefficient, xSideLength, ySideLength)

f = open("xconf.txt", "w")
f.write(conf_str)
f.close()

for i in range(0, total_number, how_many_in_single_thread):
    print(i, str(i + how_many_in_single_thread))
    p = Process(target=single_altitude_thread, args=(allCoords[i:i + how_many_in_single_thread], str(i // how_many_in_single_thread)))
    processes.append(p)


for p in processes:
    p.start()

for p in processes:
    p.join()


print(datetime.now())
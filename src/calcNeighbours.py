import time
from multiprocessing import Process

import matplotlib.pyplot as plt
import pyodbc
from funsToCalcNeighbours import *



def get_sql_from_parcels_with_neighbours(points_with_neighbours):
    result_sql = ""
    for point in points_with_neighbours:
        result_sql += generate_insert_statements_for_single_point(point)
    return result_sql

def generate_insert_statements_for_single_point(point_with_neighbours):
    result_sql = ""
    for neighbour in point_with_neighbours[7]:
        result_sql += generate_single_insert_statement(point_with_neighbours[0], point_with_neighbours[5], neighbour)
    return result_sql

def generate_single_insert_statement(point, points_shape, neighbour):
    return "insert into neighbour2 (parcel_id, parcel_shape, neighbour_id, neighbour_shape) values ({}, geometry::STGeomFromText(\'{}\', 2229) , {}, geometry::STGeomFromText(\'{}\', 2229));\n".format(point,points_shape, neighbour[0], neighbour[1])

def process_procedure(parcels_list, pieces_map, id):
    parcels_with_neighbours = get_parcels_with_neighbours(parcels_list, pieces_map)
    sql = get_sql_from_parcels_with_neighbours(parcels_with_neighbours)
    name = "insert" + str(id) + ".txt"
    with open(name, "w") as text_file:
        text_file.write(sql)

if __name__ == '__main__':
    cursor = get_cursor()

    # parcels are tuples: (id, latitude, longitude, pieceNumber, neighbours_list)
    parcels = get_all_parcels(cursor)

    # pieces map is dictionary, piece_id is key, value is tuple: (list_of_parcels_of_this_piece, list_of_neighbours_of_this_piece)
    pieces_map = get_pieces_map(parcels)

    procs = []

    start = time.time()
    # for i in range(0,len(parcels)//1000):
    pr = Process(target=process_procedure, args=(parcels[5000:7000],pieces_map, 1))
    pr.start()
    procs.append(pr)
    # for pc in procs:
    pr.join()

    stop = time.time()
    print(stop - start)



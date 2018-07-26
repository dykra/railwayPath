import pyodbc
import time

from geopy import distance


def get_cursor():
    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server=DAWID-PC\SQLEXPRESS;"
                          "Database=LosAngelesCounty;"
                          "Trusted_Connection=yes;")

    cursor = cnxn.cursor()
    return cursor


def get_parcels_to_check(piece_id, pieces_map):
    keys = pieces_map.keys()
    result = []
    map_element = tuple(pieces_map[piece_id])
    result.extend(map_element[1])
    for neighbour in map_element[0]:
        if (neighbour in keys):
            result.extend(pieces_map[neighbour][1])

    return result

def get_distance_between_parcels_in_kilometers(parcel1, parcel2):
    p1Coords = (parcel1[1], parcel1[2])
    p2Coords = (parcel2[1], parcel2[2])
    return distance.distance(p1Coords, p2Coords).km


def get_parcels_with_neighbours(parcels, pieces_map):
    print("getting")
    j = 0
    print(len(parcels))
    for p in parcels:
        j += 1
        if (j % 50 == 0):
            print(j)
        piece_id = p[3]
        parcels_to_check = []
        parcels_to_check = list(get_parcels_to_check(piece_id, pieces_map))

        for ptc in parcels_to_check:
            ptc[6] = (get_distance_between_parcels_in_kilometers(p,ptc))
        result_neighbours = sorted(parcels_to_check, key=lambda x: x[6])[:11]

        p[7] = list([[r[0],r[5]] for r in result_neighbours])

    return parcels



def get_pieces_map(parcels):
    prev = 0
    result = {}
    for p in parcels:
        # p[2] is piece number of parcel
        if (p[3] != prev):
            result[p[3]] = (p[4], [p])
            prev = p[3]
        else:
            result[p[3]][1].append(p)
        # print(result)
    return result

def convert_neighbours(row):
    neigh_list = list(map(int, row[4].split(',')))
    row[4] = neigh_list
    # row.append(0.0)
    # row.append([])
    return list(row)


def get_all_parcels(cursor):
    parcels = []
    print("will be downloading")
    cursor.execute('select top 200000 ieraobjectid, CAST(center_lat as float), CAST(center_lon as float), pieceNumber, neighbours_str, shapeAsText '
                   'from dbo.parcel '
                   'where CENTER_LAT != 0 and CENTER_LON != 0 '
                   'order by pieceNumber')
    i = 0
    print("downloaded")
    for row in cursor:
        new_row = convert_neighbours(row)
        new_row.append(0.0)
        new_row.append([])
        parcels.append(new_row)
        i = i + 1
        if (i % 10000 == 0):
            print("Done ", i)
    return parcels

# median of areas
# cursor.execute('declare @Median int; '
#                'SELECT @Median = PERCENTILE_CONT(0.5) '
#                'WITHIN GROUP (ORDER BY Shape.STArea()) '
#                'OVER () '
#                'FROM dbo.FILTERED_PARCEL; '
#                'SELECT @Median')
# median = 0.0
#
# for row in cursor:
#     median = int(row[0])
#     print(median)
import matplotlib.pyplot as plt
import pyodbc
from funs import *


cursor = get_cursor()

# parcels are tuples: (id, latitude, longitude, pieceNumber, neighbours_list)
parcels = get_all_parcels(cursor)

# pieces map is dictionary, piece_id is key, value is tuple: (list_of_parcels_of_this_piece, list_of_neighbours_of_this_piece)
pieces_map = get_pieces_map(parcels)



parcels_with_neighbours = get_parcels_with_neighbours(parcels, pieces_map)
print(parcels_with_neighbours)






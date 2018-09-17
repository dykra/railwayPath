date_limit = 20150000
excluded_values = [0, 9, 999999999]
seed = 7

#  ----------  You have to enable TCP/IP connection to SQL Server in SQL Server Configuration Manager.

#  ----------  Windows Authentication
driver = "{SQL Server Native Client 11.0}"
server = "DESKTOP-C1V4R2D"
database = "LosAngelesCounty"

connection_string_WindowsAuth = "Driver={}; Server={}; Database={}; Trusted_Connection=yes;"\
    .format(driver, server, database)

connection_string = ("Driver={SQL Server Native Client 11.0};"
                          "Server=DESKTOP-C1V4R2D;"
                          "Database=LosAngelesCounty;"
                          "Trusted_Connection=yes;")

#  ----------  SQL Authentication
database_password = ''
create_loggers_helper = ""

path_weights = './../../src/resources/init_weights.hdf5'
prediction_prices_model = './../priceestimation/trained_models/500tys_1mlnn.h5'
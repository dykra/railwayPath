
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
database_password = ""
create_loggers_helper = ""

# ----------------------------------------------------------------------------------------------------


import sys
import pyodbc 
import pandas as pd


# --reading arguments
mode = ''

argv = sys.argv


print(argv[1])
arg = argv[1]
if arg == 'help':
    print('Main.py -mode 1 (connect to database) or Main.py -mode 2 (read from csv)')
    sys.exit()
elif arg == '1':
    mode = 1
elif arg == '2':
    mode = 2
else:
    print('No such mode')
    sys.exit(2)

print('Chosen mode is: ', mode)

# you have to enable TCP/IP connection to SQL Server in SQL Server Configuration Manager
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                  "Server=VIOLA;"
                  "Database=LosAngelesCounty;"
                  #"UID=dev;" - TODO
                  #"PWD=xyz;")
                  "Trusted_Connection=yes;")


#cursor = cnxn.cursor()
#cursor.execute('SELECT * FROM Lands_Vectors')

#for row in cursor:
#    print('row = %r' % (row,))


if mode == 1:
    df = pd.read_sql_query('SELECT * FROM Lands_Vectors', cnxn)
elif mode == 2:
    file = r'resources/Lands_Vectors.csv'
    df = pd.read_csv(file, delimiter=';')

print('---Data loaded---')

X = df.iloc[:, 1:10].values
Y = df.iloc[:, 11].values
print(X)

#for row in df:
#   print('row = %r' % (row,))




import sys
import pyodbc

import pandas as pd
import tensorflow as tf
import tensorflow.python# import pywrap_tensorflow
from keras.models import Sequential
from keras.layers import Dense
import numpy

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


# ---------     Load data to DataFrame
if mode == 1:
    df = pd.read_sql_query('SELECT * FROM Lands_Vectors', cnxn)
elif mode == 2:
    file = r'resources/Lands_Vectors.csv'
    df = pd.read_csv(file, delimiter=';')

print('---Data loaded---')

# split into X set and Y set
X = df.iloc[:, 1:51]
Y = df.iloc[:, 52]


print(X)
print('-------')
print(Y)

# ---------   Define model
# sequence of layers
#  we will use a fully-connected network structure with three layers.
#
# Fully connected layers are defined using the Dense class

# We can specify the number of neurons in the layer as the first argument,
#  the initialization method as the second argument as init and specify
# the activation function using the activation argument.

# create model
model = Sequential()
model.add(Dense(12, input_dim=50, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


# Fit the model
model.fit(X, Y, epochs=150, batch_size=51)



# evaluate the model
scores = model.evaluate(X, Y)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

# evaluate the model
scores = model.evaluate(X, Y)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
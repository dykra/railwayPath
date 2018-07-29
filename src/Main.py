
import sys
import pyodbc

import pandas as pd
import tensorflow as tf
import tensorflow.python# import pywrap_tensorflow
from keras.models import Sequential
from keras.layers import Dense
import numpy

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# --reading arguments
from keras.wrappers.scikit_learn import KerasRegressor

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
                  "Server=DESKTOP-C1V4R2D;"
                  "Database=LosAngelesCounty;"
                  "Trusted_Connection=yes;")


# ---------     Load data to DataFrame
if mode == 1:
    df = pd.read_sql_query('select * from PARCEL_DATA_SET', cnxn)
elif mode == 2:
    file = r'resources/Lands_Vectors.csv'
    df = pd.read_csv(file, delimiter=';')

print('---Data loaded---')

# split into X set and Y set było 68
X = df.iloc[:, 1:71]
Y = df.iloc[:, 71]
## 52
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

##model.add(Dense(12, input_dim=67, activation='relu'))
##model.add(Dense(8, activation='relu'))
##model.add(Dense(1, activation='sigmoid')),, było 67
# input_dim - set it to 8 for the 8 input variables

model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
model.add(Dense(1, kernel_initializer='normal'))


# Compile model
#model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
model.compile(loss='mean_squared_error', optimizer='adam')

print('Ok-1')
# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)
# evaluate model with standardized dataset
estimator = KerasRegressor(build_fn=model, epochs=100, batch_size=1, verbose=0)
print('Ok-2')

kfold = KFold(n_splits=2, random_state=seed)
print('Ok-3')

#checkpoint = ModelCheckpoint("debug.hdf", monitor="val_loss", verbose=1, save_best_only=True, mode="save_weights_only")



#tu się wywala:


results = cross_val_score(estimator, X.values, Y.values, cv=kfold, n_jobs=1)
print('Ok-4')
#print("Results: %.2f (%.2f) MSE" % (results.mean(), results.std()))
print('Ok-5')



# Fit the model
#model.fit(X, Y, epochs=150, batch_size=
# epochs - number of iterations


#model.fit(X, Y, epochs=100, batch_size=32)



# evaluate the model

#scores = model.evaluate(X, Y)
#print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))




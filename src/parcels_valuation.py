import sys
import pyodbc
import pandas as pd
import tensorflow as tf
from keras.losses import mean_squared_error, mean_absolute_percentage_error
from keras.models import Sequential
from keras.layers import Dense, K
import numpy
from matplotlib import pyplot
import logging
from keras.callbacks import ModelCheckpoint

""" 
    Global variables
"""

date_limit = 20150000
excluded_values = [0, 9, 999999999]
basic_query = ("SELECT * FROM PARCEL_VECTORS"
        " WHERE Sale_Amount < {} and Sale_Amount > {}"
        " and LS1_Sale_Date > {}" 
        " and Sale_Amount != {} and Sale_Amount != {} and Sale_Amount != {}")


"""
    Model is defined in this function.
    
    To create model should be specified sequence of layers.
    In each layer can be specified the number of neurons (first arg),
    the initialization method (second arg) as init and specified
    the activation function using the activation argument.       
    
:returns: Model
    
"""


def baseline_model_for_to_500tys_and_above_1mln():
    model = Sequential()
    model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
    model.add(Dense(50, kernel_initializer='normal'))
    model.add(Dense(1, kernel_initializer='normal'))
    
    model.load_weights("init_weights.hdf5")

    model.compile(loss=mean_squared_error, optimizer='adam',
                  metrics=['mean_squared_error',
                           'mean_absolute_error',
                           'mean_absolute_percentage_error'])
    return model


"""
    0 bucket: lower_limit = 0, upper_limit = 500000
    1 bucket: lower_limit = 500000, upper_limit = 1000000
    2 bucket: lower_limit = 1000000, upper_limit = 200000000

"""


def get_one_bucket_data(cnxn, lower_limit, upper_limit):
    query = basic_query.\
        format(upper_limit, lower_limit, date_limit, excluded_values[0], excluded_values[1], excluded_values[2])
    if lower_limit == 0:
        result = pd.read_sql(query + " and Price_Per_Single_Area_Unit >= 1", cnxn)
    else:
        result = pd.read_sql(query, cnxn)
    return result


def main():
    #  ----------  Set logger
    logger_format = '%(asctime)-15s s -8s %(message)s'
    logging.basicConfig(format=logger_format)

    #  ----------  Reading arguments

    driver = "{SQL Server Native Client 11.0}"
    server = "DESKTOP-C1V4R2D"
    database = "LosAngelesCounty"

    #  ----------  You have to enable TCP/IP connection to SQL Server in SQL Server Configuration Manager.
    connection_string = "Driver={}; Server={}; Database={}; Trusted_Connection=yes;".format(driver, server, database)
    cnxn = pyodbc.connect(connection_string)

    df = get_one_bucket_data(cnxn, 0, 500000)

    logging.info('--= Data loaded =--')

    # split into X set and Y set było 71
    x = df.iloc[:, 1:71]
    y = df.iloc[:, 71]

    logging.info('--= X set =--')
    print(x)
    logging.info('--= Y set =--')
    print(y)

    #  ----------  Fix random seed for reproducibility
    seed = 7

    numpy.random.seed(seed)

    model = baseline_model_for_to_500tys_and_above_1mln()
    filepath = "500tys_1mln-PV.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    callbacks_list = [checkpoint]
#9000
    results = model.fit(x.values, y.values, epochs=200, batch_size=len(x.values), validation_split=0.1,
                        callbacks=callbacks_list,
                        verbose=2)

    logging.info('--= Plot metrics =--')
    pyplot.plot(results.history['mean_squared_error'])
    pyplot.show()
    pyplot.plot(results.history['mean_absolute_error'])
    pyplot.show()
    pyplot.plot(results.history['mean_absolute_percentage_error'])
    pyplot.show()
    pyplot.plot(results.history['cosine_proximity'])
    pyplot.show()
    logging.info('--= Model counted. =--')

    prediction = model.predict(x.values)
    print('First prediction:', prediction[0])

    logging.info('--= Model summary: =--')
    model.summary()

    model.save('500tys_1mln-PV.h5')
    logging.info('--= Model saved in test_with_lattitude_and_longitude.h5 file. =--')


if __name__ == '__main__':
    main()

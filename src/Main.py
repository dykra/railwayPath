import sys
import pyodbc
import pandas as pd
import tensorflow as tf
from keras.losses import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, K
import numpy
from matplotlib import pyplot
import logging


"""
    Model is defined in this function.
    
    To create model should be specified sequence of layers.
    In each layer can be specified the number of neurons (first arg),
    the initialization method (second arg) as init and specified
    the activation function using the activation argument.       
    
:returns: Model
    
"""


def baseline_model():
    model = Sequential()
    model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss=mean_squared_error, optimizer='adam',
                  metrics=['mean_squared_error',
                           'mean_absolute_error', 'mean_absolute_percentage_error',
                           'cosine_proximity'])
    return model


def main():
    #  ----------  Set logger
    logger_format = '%(asctime)-15s s -8s %(message)s'
    logging.basicConfig(format=logger_format)

    #  ----------  Reading arguments
    logging.info('--= Read arguments =--')
    # TODO: https://docs.python.org/3/library/argparse.html
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

    logging.info('--= Chosen mode is: %s =--', mode)

    #  ----------  You have to enable TCP/IP connection to SQL Server in SQL Server Configuration Manager.
    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server=DESKTOP-C1V4R2D;"
                          "Database=LosAngelesCounty;"
                          "Trusted_Connection=yes;")

    #  ----------  Load data to DataFrame
    if mode == 1:
        df = pd.read_sql_query('''
            SELECT *
            FROM LosAngelesCounty.dbo.PARCEL_DATA_SET
            WHERE Sale_Amount <1000000 AND Sale_Amount > 500000
          ''', cnxn)
    elif mode == 2:
        file = 'resources/Lands_Vectors.csv'
        df = pd.read_csv(file, delimiter=',')

    logging.info('--= Data loaded =--')

    # split into X set and Y set było 68
    x = df.iloc[:, 1:71]
    y = df.iloc[:, 71]

    logging.info('--= X set =--')
    print(x)
    logging.info('--= Y set =--')
    print(y)

    #  ----------  Fix random seed for reproducibility
    seed = 7
    numpy.random.seed(seed)

    model = baseline_model()
    results = model.fit(x.values, y.values, epochs=9265, batch_size=len(x.values), verbose=2)
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

    model.save('model.h5')
    logging.info('--= Model saved in model.h5 file. =--')


if __name__ == '__main__':
    main()

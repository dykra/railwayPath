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
    model.add(Dense(50, kernel_initializer='normal'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.load_weights("withBestFit.h5")

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

    # SELECT *
    # FROM LosAngelesCounty.dbo.PARCEL_DATA_SET
    # WHERE Sale_Amount <1000000 AND Sale_Amount > 500000
    #  ----------  Load data to DataFrame
    if mode == 1:
        df = pd.read_sql_query('''
            SELECT * FROM PARCEL_VECTORS
	        WHERE Sale_Amount <200000 
	            and Price_Per_Single_Area_Unit >= 1 
	            and LS1_Sale_Date > 20150000
                and Sale_Amount != 9
                and Sale_Amount != 0
                and Sale_Amount != 999999999  
                      ''', cnxn)
    elif mode == 2:
        file = 'resources/Lands_Vectors.csv'
        df = pd.read_csv(file, delimiter=',')

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

    model = baseline_model()
    filepath = "weights.best.hdf5"
    #checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    #callbacks_list = [checkpoint]

    results = model.fit(x.values, y.values, epochs=800, batch_size=len(x.values), validation_split=0.1,
                        #callbacks=callbacks_list,
                        verbose=2)

    logging.info('--= Plot metrics =--')
    #pyplot.plot(results.history['mean_squared_error'])
    pyplot.show()
    pyplot.plot(results.history['mean_absolute_error'])
    pyplot.show()
    pyplot.plot(results.history['mean_absolute_percentage_error'])
    pyplot.show()
    #pyplot.plot(results.history['cosine_proximity'])
    pyplot.show()
    #logging.info('--= Model counted. =--')

    prediction = model.predict(x.values)

    print('First prediction:', prediction[0])

    logging.info('--= Model summary: =--')
    model.summary()

    model.save('withBestFit.h5')
    logging.info('--= Model saved in test_with_lattitude_and_longitude.h5 file. =--')


if __name__ == '__main__':
    main()

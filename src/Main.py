import sys
import pyodbc
import pandas as pd
import tensorflow as tf
from keras.losses import mean_squared_error, mean_absolute_percentage_error
from keras.models import Sequential
from keras.layers import Dense, K
import numpy
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import logging

from keras.wrappers.scikit_learn import KerasRegressor


"""
    Model is defined in this function.
    
    To create model should be specified sequence of layers.
    In each layer can be specified the number of neurons (first arg),
    the initialization method (second arg) as init and specified
    the activation function using the activation argument.       
    
:return: Model
    
"""


def baseline_model():
    model = Sequential()
    model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    # model.compile(loss='mean_squared_error', optimizer='adam')
    precision = as_keras_metric(tf.metrics.precision)
    recall = as_keras_metric(tf.metrics.recall)
    model.compile(loss=mean_absolute_percentage_error, optimizer='adam', metrics=[precision, recall])
    return model


def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))


"""
    Function to wrap tensorflow metrics.

:return: Wrapper

"""


def as_keras_metric(method):
    import functools
    from keras import backend as K

    """
            Wrapper for turning tensorflow metrics into keras metrics
    """
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        value, update_op = method(self, args, **kwargs)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value
    return wrapper


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
    seed = 2 ** 32 - 29638824
    numpy.random.seed(seed)

    #  ----------  Evaluate model with standardized dataset
    estimator = KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=1, verbose=False)

    kfold = KFold(n_splits=2, random_state=seed)

    results = cross_val_score(estimator, x.values, y.values, cv=kfold, n_jobs=1, verbose=False)

    logging.info('--= Model counted. =--')
    print("Results: %.2f (+/- %.2f) MSE" % (results.mean(), results.std() * 2))

    estimator.fit(x.values, y.values, verbose=False)

    prediction = estimator.predict(x.values)

    print('First prediction:', prediction[0])

    # print("{0:.15f}".format(mean_squared_error(prediction, Y.values)))
    print('mean_squared_error:', abs(mean_squared_error(prediction, y.values)))
    print('estimator.model.loss:', abs(estimator.model.loss(prediction, y.values)))

    logging.info('--= Model summary: =--')
    estimator.model.summary()

    scores = estimator.model.evaluate(x.values, y.values)

    print("Accuracy: %.2f%%" % scores)

    estimator.model.save('model.h5')
    logging.info('--= Model saved in model.h5 file. =--')


if __name__ == '__main__':
    main()

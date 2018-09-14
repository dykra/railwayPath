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
from src.PriceEstimator.Utils.logger_helper import create_loggers_helper
from src.PriceEstimator.Utils.database_handler import DatabaseHandler
from src.PriceEstimator.constants import connection_string_WindowsAuth, connection_string

""" 
    Global variables
"""

date_limit = 20150000
excluded_values = [0, 9, 999999999]
basic_query = ("SELECT * FROM PARCEL_VECTORS"
        " WHERE Sale_Amount < {} and Sale_Amount > {}"
        " and LS1_Sale_Date > {}" 
        " and Sale_Amount != {} and Sale_Amount != {} and Sale_Amount != {}")


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class ModelTrainer:
    # def __init__(self):
    #   self.model = "" ?? TODO

    """
        Model is defined in this function.

        To create model should be specified sequence of layers.
        In each layer can be specified the number of neurons (first arg),
        the initialization method (second arg) as init and specified
        the activation function using the activation argument.

    :returns: Model

    """

    def create_model(self):
        model = Sequential()
        model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
        model.add(Dense(50, kernel_initializer='normal'))
        model.add(Dense(1, kernel_initializer='normal'))

        model.load_weights("init_weights.hdf5")
        logger.info('Weights loaded to model.')
        model.compile(loss=mean_squared_error, optimizer='adam',
                      metrics=['mean_squared_error',
                               'mean_absolute_error',
                               'mean_absolute_percentage_error'])
        logger.info('Model created')
        return model

    """
            Function to save checkpoints.

            After each epoch, it is checked if results improved.
            If yes, new weights are saved in file.
            After whole training in file, there is save weights, 
            for witch the results were the best.

        :returns: Callbacks_list

        """

    def save_checkpoint(self, file_path):
        # file_path = "500tys_1mln-test.hdf5"
        checkpoint = ModelCheckpoint(file_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]
        return callbacks_list

    def draw_plots(self, history_object):
        logging.info('--= Plot metrics =--')
        pyplot.plot(history_object.history['mean_squared_error'])
        pyplot.show()
        pyplot.plot(history_object.history['mean_absolute_error'])
        pyplot.show()
        pyplot.plot(history_object.history['mean_absolute_percentage_error'])
        pyplot.show()
        pyplot.plot(history_object.history['cosine_proximity'])
        pyplot.show()

"""
    0 bucket: lower_limit = 0, upper_limit = 500000
    1 bucket: lower_limit = 500000, upper_limit = 1000000
    2 bucket: lower_limit = 1000000, upper_limit = 200000000

"""


def get_one_bucket_data(database_handler, lower_limit, upper_limit):

    query = basic_query.\
        format(upper_limit, lower_limit, date_limit, excluded_values[0], excluded_values[1], excluded_values[2])
    if lower_limit == 0:
        result = database_handler.execute_query(query=query + " and Price_Per_Single_Area_Unit >= 1")
    else:
        result = database_handler.execute_query(query)
    logging.info('--= Data loaded =--')
    return result


def main():

    database_handler = DatabaseHandler('', '', '', connection_string_WindowsAuth)

    df = get_one_bucket_data(database_handler, 0, 500000)

    # split into X set and Y set
    x = df.iloc[:, 1:71]
    y = df.iloc[:, 71]

    print('--= X set =--')
    print(x)
    print('--= Y set =--')
    print(y)

    #  ----------  Fix random seed for reproducibility
    seed = 7
    numpy.random.seed(seed)

    model_trainer = ModelTrainer()
    model = model_trainer.create_model()

    callbacks_list = model_trainer.save_checkpoint("500tys_1mln-test.hdf5")

    #  ----------  Model training
    results = model.fit(x.values, y.values, epochs=200, batch_size=len(x.values), validation_split=0.1,
                        callbacks=callbacks_list,
                        verbose=2)

    logging.info('--= Model summary: =--')
    model.summary()

    #  ----------  Draw plots
    model_trainer.draw_plots(history_object=results)

    #  ----------  Save model
    saved_model_file_path = '500tys_1mln-test.h5'
    model.save(saved_model_file_path)
    logging.info('--= Model saved in {} file. =--'.format(saved_model_file_path))

# TODO ... new program... price prediction

    #prediction = model.predict(x.values)
    #print('First prediction:', prediction[0])


if __name__ == '__main__':
    main()

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
from src.priceestimation.utils.logger import create_loggers_helper
from src.priceestimation.utils.database_handler import DatabaseHandler
from src.priceestimation.constants import date_limit, excluded_values, seed, path_weights, prediction_prices_model
from src.priceestimation.utils.serialization_module import serialization_object_decorate


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()

# TODO - view in the database
basic_query = ("SELECT top 1000 * FROM FILTERED_PARCEL where"
                # " WHERE Sale_Amount < {} and Sale_Amount > {} and "
                "  LS1_Sale_Date > {}" )
                # " and Sale_Amount != {} and Sale_Amount != {} and Sale_Amount != {}")


class PricePredictionModelTrainer:
    """
        Model is defined in this function.

        To create model should be specified sequence of layers.
        In each layer can be specified the number of neurons (first arg),
        the initialization method (second arg) as init and specified
        the activation function using the activation argument.

    :returns: Model

    """

    def __init__(self, weights_path, checkpoint_file_path):
        self.weights_path = weights_path
        self.checkpoint_path = checkpoint_file_path
        self.model = None
        self.checkpoint = None
        self.callback_list = None
        self.create_model()
        self.save_callback()

    def create_model(self):
        self.model = Sequential()
        self.model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
        self.model.add(Dense(50, kernel_initializer='normal'))
        self.model.add(Dense(1, kernel_initializer='normal'))

        self.model.load_weights(self.weights_path)
        logger.info('Weights loaded to model.')
        self.model.compile(loss=mean_squared_error, optimizer='adam',
                           metrics=['mean_squared_error',
                                    'mean_absolute_error',
                                    'mean_absolute_percentage_error'])
        logger.info('Model created')

    """
            Function to save checkpoints.

            After each epoch, it is checked if results improved.
            If yes, new weights are saved in file.
            After whole training in file, there is save weights, 
            for witch the results were the best.

        :returns: Callbacks_list

        """

    def save_callback(self):
        self.callback_list = [ModelCheckpoint(self.checkpoint_path, monitor='val_loss',
                                              verbose=1, save_best_only=True, mode='min')]

    def fit_the_model(self, training_x_values, training_y_values,
                      batch_size, epochs=200, validation_split=0.1, verbose=2):
        #  ----------  Fix random seed for reproducibility
        numpy.random.seed(seed)
        return self.model.fit(training_x_values, training_y_values,
                              batch_size=batch_size, validation_split=validation_split,
                              callbacks=self.callback_list, verbose=verbose, epochs=epochs)

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


# TODO - change it into view not building query
def get_one_bucket_data(database_handler, lower_limit, upper_limit):
    query = basic_query.\
        format(upper_limit, lower_limit, date_limit, excluded_values[0], excluded_values[1], excluded_values[2])
    if lower_limit == 0:
        result = database_handler.execute_query(query=query)  #    + " and Price_Per_Single_Area_Unit >= 1")
    else:
        result = database_handler.execute_query(query)
    logging.info('--= Data loaded =--')
    return result


def serialize_price_estimator_model(file_name, model):
    model.save(file_name)
    logging.info('--= Model saved in {} file. =--'.format(file_name))


def deserialize_price_estimator_model(file_name):
    logger.info('DESERIALIZE')
    pass
    # TODO - reload model from file and return this

# TODO - database handler provide as argument while creating model
# TODO - after few execution change parameter_value
@serialization_object_decorate(serialize_function=serialize_price_estimator_model,
                               deserialize_function=deserialize_price_estimator_model,
                               file_path=prediction_prices_model
                               )
def prepare_price_estimator_model(lower_limit=0, upper_limit=500000):
    logger.info('CREATING MODEL')
    model_trainer = PricePredictionModelTrainer(weights_path=path_weights,
                                                checkpoint_file_path='resources/500tys_1mln-test.hdf5')

    database_handler = DatabaseHandler(server='localhost', user_name='SA', database_name='LA_County_DB')

    data_frame = get_one_bucket_data(database_handler, lower_limit, upper_limit)

    # TODO - is there a way to automate counting this values?
    # split into X set and Y set
    x = data_frame.iloc[:, 1:71]
    y = data_frame.iloc[:, 71]

    # print('--= X set =--')
    # print(x)
    # print('--= Y set =--')
    # print(y)

    #  ----------  Model training
    # TODO - move to constants
    results = model_trainer.fit_the_model(training_x_values=x.values, training_y_values=y.values,
                                          batch_size=len(x.values), epochs=200, validation_split=0.1, verbose=2)
    #
    # logging.info('--= Model summary: =--')
    # model_trainer.model.summary(results)

    return model_trainer


def main():
    model = prepare_price_estimator_model()

    #  ----------  Draw plots
    # model.draw_plots(history_object=results)

    #  ----------  Save model
    # saved_model_file_path = './trained_models/500tys_1mln-test.h5'
    # model.save(saved_model_file_path)


    #prediction = model.predict(x.values)
    #print('First prediction:', prediction[0])


if __name__ == '__main__':
    main()

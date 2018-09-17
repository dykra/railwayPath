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
from src.priceestimation.constants import connection_string_WindowsAuth, date_limit, excluded_values
from src.priceestimation.utils.serialization_module import serialization_object_decorate


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()

# TODO - view in the database
basic_query = ("SELECT * FROM FILTERED_PARCEL where"
                # " WHERE Sale_Amount < {} and Sale_Amount > {} and "
                "  LS1_Sale_Date > {}" )
                # " and Sale_Amount != {} and Sale_Amount != {} and Sale_Amount != {}")


# TODO - ujednolicic czy zwrocenie samego modelu wusyarczy do zapisywania tych ceckpoint
class PricePredictionModelTrainer:
    """
        Model is defined in this function.

        To create model should be specified sequence of layers.
        In each layer can be specified the number of neurons (first arg),
        the initialization method (second arg) as init and specified
        the activation function using the activation argument.

    :returns: Model

    """

    def __init__(self):
        self.model = None
        self.checkpoint = None

    def create_model(self):
        self.model = Sequential()
        self.model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
        self.model.add(Dense(50, kernel_initializer='normal'))
        self.model.add(Dense(1, kernel_initializer='normal'))

        self.model.load_weights("./../../src/resources/init_weights.hdf5")
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

    def save_checkpoint(self, file_path):
        self.checkpoint = ModelCheckpoint(file_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [self.checkpoint]
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
    # TODO - reload model from file
    # return model


@serialization_object_decorate(file_path='./../priceestimation/trained_models/500tys_1mln.h5',
                               serialize_function=serialize_price_estimator_model,
                               deserialize_function=deserialize_price_estimator_model)
def prepare_price_estimator_model():
    logger.info('CREATING MODEL')
    model_trainer = PricePredictionModelTrainer()
    model_trainer.create_model()

    callbacks_list = model_trainer.save_checkpoint("resources/500tys_1mln-test.hdf5")

    database_handler = DatabaseHandler(server='localhost', user_name='SA', database_name='LA_County_DB')

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
    #  ----------  Model training
    results = model_trainer.model.fit(x.values, y.values, epochs=200, batch_size=len(x.values), validation_split=0.1,
                        callbacks=callbacks_list,
                        verbose=2)

    logging.info('--= Model summary: =--')
    model_trainer.model.summary()

    return model_trainer

# TODO - database handler provide as argument while creating model


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

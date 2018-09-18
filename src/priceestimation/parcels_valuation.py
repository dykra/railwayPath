from keras.losses import mean_squared_error, mean_absolute_percentage_error
from keras.models import Sequential
from keras.layers import Dense, K
import numpy
from matplotlib import pyplot
import logging
from keras.callbacks import ModelCheckpoint
from src.priceestimation.utils.logger import create_loggers_helper
from src.priceestimation.utils.database_handler import DatabaseHandler
from src.priceestimation.configuration_constants import *
from src.priceestimation.database_connection_constants import *
from src.priceestimation.utils.serialization_module import serialization_object_decorate, update_bucket_type


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def generate_file_name_with_price_limit(base_name, type, extension='.h5'):
    return base_name + str(type) + extension


# TODO - view in the database
basic_query = ("SELECT top 1000 * FROM FILTERED_PARCEL where"
                # " WHERE Sale_Amount < {} and Sale_Amount > {} and "
                "  LS1_Sale_Date > {}" )
                # " and Sale_Amount != {} and Sale_Amount != {} and Sale_Amount != {}")


def draw_plots(history_object):
    logging.info('--= Plot metrics =--')
    pyplot.plot(history_object.history['mean_squared_error'])
    pyplot.show()
    pyplot.plot(history_object.history['mean_absolute_error'])
    pyplot.show()
    pyplot.plot(history_object.history['mean_absolute_percentage_error'])
    pyplot.show()
    pyplot.plot(history_object.history['cosine_proximity'])
    pyplot.show()


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
                      batch_size, epochs=epochs_value, validation_split=validation_split_value, verbose=verbose_value):
        #  ----------  Fix random seed for reproducibility
        numpy.random.seed(seed)
        return self.model.fit(training_x_values, training_y_values,
                              batch_size=batch_size, validation_split=validation_split,
                              callbacks=self.callback_list, verbose=verbose, epochs=epochs)


def serialize_price_estimator_model(file_name, model_trainer):
    model_trainer.model.save(file_name)
    logging.info('--= Model saved in {} file. =--'.format(file_name))


# TODO - reload model from file and return this
def deserialize_price_estimator_model(file_name):
    logger.info('Model ' + file_name + ' is being deserialized.')
    pass


@serialization_object_decorate(serialize_function=serialize_price_estimator_model,
                               deserialize_function=deserialize_price_estimator_model,
                               )
def prepare_price_estimator_model(execute_view_query, database_handler):
    logger.info('CREATING MODEL')
    model_trainer = PricePredictionModelTrainer(weights_path=weights_file_path,
                                                checkpoint_file_path=checkpoint_file_path)

    data_frame = database_handler.execute_query(execute_view_query)# get_one_bucket_data(database_handler, lower_limit, upper_limit)

    # split into X set and Y set
    x = data_frame.iloc[:, 1:71]
    y = data_frame.iloc[:, 71]

    # print('--= X set =--')
    # print(x)
    # print('--= Y set =--')
    # print(y)

    #  ----------  Model training
    results = model_trainer.fit_the_model(training_x_values=x.values, training_y_values=y.values,
                                          batch_size=len(x.values), epochs=epochs_value,
                                          validation_split=validation_split_value, verbose=verbose_value)
    #
    # logging.info('--= Model summary: =--')
    # model_trainer.model.summary(results)
    # draw_plots(history_object=results)

    return model_trainer.model


def main():
    database_handler = DatabaseHandler(server=server, user_name=user_name, database_name=database_name)
    for set_type in classification_buckets:
        update_bucket_type(bucket_type=generate_file_name_with_price_limit(base_name=prediction_prices_model_file_path,
                                                                           type=set_type))
        # TODO - procedure query execute with parameter
        model = prepare_price_estimator_model(execute_view_query='SELECT * FROM PROCEDURE(' + set_type + ')',
                                              database_handler=database_handler)

        # prediction = model.predict(x.values)
        # print('First prediction:', prediction[0])
        # TODO - save predictions to the database (in other program)
        # TODO - predict for all rows from database (in other program)


if __name__ == '__main__':
    main()

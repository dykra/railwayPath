from keras.losses import mean_squared_error, mean_absolute_percentage_error
from keras.models import Sequential, load_model
from keras.layers import Dense, K
import numpy
import logging
import sys
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


def generate_file_name_with_price_limit(base_name, bucket_type, extension='.h5'):
    return base_name + '1mln_200mln.h5'#str(bucket_type) + extension


class PricePredictionModelTrainer:

    def __init__(self, weights_path, checkpoint_file_path_input):
        self.weights_path = weights_path
        self.checkpoint_path = checkpoint_file_path_input
        self.model = None
        self.checkpoint = None
        self.callback_list = None
        self.create_model()
        self.save_callback()

    """
        Model is defined in this function.
        To create model should be specified sequence of layers.
        In each layer can be specified the number of neurons (first arg),
        the initialization method (second arg) as init and specified
        the activation function using the activation argument.

    """
    def create_model(self):
        self.model = Sequential()
        self.model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
        self.model.add(Dense(50, kernel_initializer='normal'))
        self.model.add(Dense(1, kernel_initializer='normal'))

        try:
            self.model.load_weights(self.weights_path)
        except OSError:
            logger.error('Problem with reading the file {}'.format(self.weights_path))
            sys.exit(1)
        logger.debug('Weights loaded to model.')
        self.model.compile(loss=mean_squared_error, optimizer='adam',
                           metrics=['mean_squared_error',
                                    'mean_absolute_error',
                                    'mean_absolute_percentage_error'])
        logger.info('Model is created.')

    """
        Function to save checkpoints.

        After each epoch, it is checked if results improved.
        If yes, new weights are saved in file.
        After whole training in file, there is save weights, 
        for witch the results were the best.

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
    logging.info('Model saved in {} file.'.format(file_name))


def deserialize_price_estimator_model(file_name):
    logger.info('Model ' + file_name + ' is being deserialized.')
    return load_model(file_name)


@serialization_object_decorate(serialize_function=serialize_price_estimator_model,
                               deserialize_function=deserialize_price_estimator_model,
                               )
def prepare_price_estimator_model(execute_view_query, database_handler, bucket_type):
    logger.info('CREATING MODEL')
    model_trainer = PricePredictionModelTrainer(weights_path=weights_file_path,
                                                checkpoint_file_path_input=generate_file_name_with_price_limit(
                                                    checkpoint_file_path, extension='.hdf5', bucket_type=bucket_type))

    data_frame = database_handler.execute_query(execute_view_query)

    # split into X set and Y set
    x = data_frame.iloc[:, 1:71]
    y = data_frame.iloc[:, 71]

    results = model_trainer.fit_the_model(training_x_values=x.values, training_y_values=y.values,
                                          batch_size=len(x.values), epochs=epochs_value,
                                          validation_split=validation_split_value, verbose=verbose_value)

    logging.info('Model summary:')
    model_trainer.model.summary(results)
    return model_trainer.model


def main():
    database_handler = DatabaseHandler(server=server, user_name=user_name, database_name=database_name)
    for set_type in classification_buckets:
        update_bucket_type(bucket_type=generate_file_name_with_price_limit(base_name=prediction_prices_model_file_path,
                                                                           bucket_type=set_type))
        model = prepare_price_estimator_model(execute_view_query="EXEC dbo.getTrainingDataPriceEstimation "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                              .format(date_limit,
                                                      set_type,
                                                      excluded_values),
                                              database_handler=database_handler,
                                              bucket_type=set_type)

        # prediction = model.predict(x.values)
        # print('First prediction:', prediction[0])
        # TODO - save predictions to the database (in other program)
        # TODO - predict for all rows from database (in other program)


if __name__ == '__main__':
    main()

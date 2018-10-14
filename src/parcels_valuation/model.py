import numpy
import logging
import sys
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.losses import mean_squared_error
from keras.callbacks import ModelCheckpoint
from src.parcels_valuation.utils.logger import create_loggers_helper
from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.utils.serialization_module import serialization_object_decorate


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def make_file_name(base_name, _limit_date, bucket, extension='.h5'):
    return base_name + str(_limit_date) + '_' + bucket + extension


class ModelTrainer:

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
                               deserialize_function=deserialize_price_estimator_model
                               )
def get_model(sp_get_date_to_train_model, database_handler, model_file_name):
    logger.info('Creation of model.')
    model_trainer = ModelTrainer(weights_path=weights_file_path,
                                 checkpoint_file_path_input=model_file_name)

    # type: dataframe
    data_to_train_model = database_handler.execute_query(sp_get_date_to_train_model)

    # split into X set and Y set
    x = data_to_train_model.iloc[:, 1:71]
    y = data_to_train_model.iloc[:, 71]

    results = model_trainer.fit_the_model(training_x_values=x.values, training_y_values=y.values,
                                          batch_size=len(x.values), epochs=epochs_value,
                                          validation_split=validation_split_value, verbose=verbose_value)

    logging.info('Model summary:')
    model_trainer.model.summary(results)
    return model_trainer.model

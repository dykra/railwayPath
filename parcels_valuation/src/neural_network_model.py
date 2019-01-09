import numpy
import logging
import sys
from keras.models import Sequential
from keras.layers import Dense
from keras.losses import mean_squared_error
from keras.callbacks import ModelCheckpoint

from utils.file_names_builder import get_checkpoints_filename, get_model_filename
from utils.logger import create_loggers_helper
from configuration.configuration_constants import weights_file_path, \
    epochs_value, validation_split_value, verbose_value, seed, train_model_with_price_parameters


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class Model:

    def __init__(self):
        self.weights_path = weights_file_path
        self.checkpoint_path = get_checkpoints_filename()
        self.model = None
        self.checkpoint = None
        self.callback_list = None

    """
        Model is defined in this function.
        To create model should be specified sequence of layers.
        In each layer can be specified the number of neurons (first arg),
        the initialization method (second arg) as init and specified
        the activation function using the activation argument.

    """

    def create_model(self):
        self.model = Sequential()
        if train_model_with_price_parameters:
            self.model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
        else:
            self.model.add(Dense(67, input_dim=67, kernel_initializer='normal', activation='relu'))
        self.model.add(Dense(50, kernel_initializer='normal'))
        self.model.add(Dense(1, kernel_initializer='normal'))

        try:
            self.model.load_weights(self.weights_path)
        except OSError:
            logger.error('Problem with reading the file {}'.format(self.weights_path))
            sys.exit(1)
        logger.debug('Weights {} loaded to model.'.format(self.weights_path))
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

    def fit_model(self, training_x_values, training_y_values,
                  batch_size, epochs=epochs_value, validation_split=validation_split_value, verbose=verbose_value):
        #  ----------  Fix random seed for reproducibility
        numpy.random.seed(seed)
        return self.model.fit(training_x_values, training_y_values,
                              batch_size=batch_size, validation_split=validation_split,
                              callbacks=self.callback_list, verbose=verbose, epochs=epochs)

    def save_model(self):
        my_filename = get_model_filename()
        self.model.save(my_filename)
        logging.info('Model saved in {} file.'.format(my_filename))

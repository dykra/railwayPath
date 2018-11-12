import logging
import os
import sys

from src.parcels_valuation.file_names_builder import get_model_filename
from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.logger import create_loggers_helper
from src.parcels_valuation.configuration.configuration_constants import limit_date, excluded_values, weights_file_path, \
    model_target_folder, validation_split_value, verbose_value, epochs_value, current_bucket, model_overwrite, \
    file_names_convention
from src.parcels_valuation.neural_network_model import Model
from src.parcels_valuation.utils.plots import draw_plots


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def train_model_decorator():
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            model_filename = get_model_filename()
            if os.path.exists(model_filename) and not model_overwrite:
                logger.error('Model exists. To overwrite set model_overwrite constant to True '
                             'in configuration_constants.py')
                return 0
            trained_model = func(*args, **kwargs)
            # trained_model.save_model()
            return trained_model

        return func_wrapper

    return decorator


@train_model_decorator()
def train_model(database_handler):
    logger.info('Creation of model.')
    neural_network_model = Model()
    neural_network_model.create_model()
    neural_network_model.save_callback()
    # type: dataframe
    data_to_train_model = database_handler.execute_query("EXEC dbo.GetDateToTrainModelWithoutPrice "
                                                         "@LimitDate = {}, "
                                                         "@BucketType={}, "
                                                         "@ExcludedList='{}'"
                                                         .format(limit_date,
                                                                 current_bucket,
                                                                 excluded_values))

    # split into X set and Y set
    x = data_to_train_model.iloc[:, 1:68] # 71
    y = data_to_train_model.iloc[:, 68]

    results = neural_network_model.fit_model(training_x_values=x.values, training_y_values=y.values,
                                             batch_size=len(x.values), epochs=epochs_value,
                                             validation_split=validation_split_value, verbose=verbose_value)

    logging.info('Model summary:')
    neural_network_model.model.summary()
    draw_plots(history_object=results)
    neural_network_model.save_model()
    return neural_network_model.model


def main():
    database_handler = DatabaseHandler()
    try:
        # for bucket in classification_buckets:
        train_model(database_handler=database_handler)
    finally:
        database_handler.close_connection()


if __name__ == '__main__':
    main()

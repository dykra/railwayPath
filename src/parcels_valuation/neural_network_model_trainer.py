import logging
import os

from src.parcels_valuation.utils.file_names_builder import get_model_filename
from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.logger import create_loggers_helper
from src.parcels_valuation.configuration.configuration_constants import limit_date, excluded_values, \
    validation_split_value, verbose_value, epochs_value, current_bucket, model_overwrite, \
    train_model_with_price_parameters
from src.parcels_valuation.neural_network_model import Model
from src.parcels_valuation.utils.plots import draw_plots
from src.parcels_valuation.utils.prices_mapping import parcel_prices_mapping


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
            return trained_model
        return func_wrapper
    return decorator


@train_model_decorator()
def train_model(database_handler):
    logger.info('Creation of model.')
    neural_network_model = Model()
    neural_network_model.create_model()
    neural_network_model.save_callback()
    if train_model_with_price_parameters:
        procedure = 'GetDateToTrainModel'
    else:
        procedure = 'GetDateToTrainModelWithoutPriceParameters'
    # Type: dataframe
    data_to_train_model = database_handler.execute_query("EXEC dbo.{} "
                                                         "@LimitDate = {}, "
                                                         "@BucketType={}, "
                                                         "@ExcludedList='{}'"
                                                         .format(procedure,
                                                                 limit_date,
                                                                 parcel_prices_mapping[current_bucket],
                                                                 excluded_values))

    # Pandas DataFrame.shape return a tuple representing the dimensionality of the DataFrame
    data_size = data_to_train_model.shape[1]
    # Split into X set and Y set
    # Take all columns except the first one - OBJECID and the last one - Sale_Amount
    x = data_to_train_model.iloc[:, 1: data_size - 1]
    y = data_to_train_model.iloc[:, data_size - 1]

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
        train_model(database_handler=database_handler)
    finally:
        database_handler.close_connection()


if __name__ == '__main__':
    main()

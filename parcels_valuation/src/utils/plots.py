import logging
from matplotlib import pyplot
from parcels_valuation.src.utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def draw_plots(history_object):
    logger.debug('Drawing plots for history_object.')
    pyplot.plot(history_object.history['mean_squared_error'])
    pyplot.show()
    pyplot.plot(history_object.history['mean_absolute_error'])
    pyplot.show()
    pyplot.plot(history_object.history['mean_absolute_percentage_error'])
    pyplot.show()

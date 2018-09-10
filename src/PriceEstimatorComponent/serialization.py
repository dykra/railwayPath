import pickle
import logging
from src.PriceEstimatorComponent.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def serialize_class(file_name, class_object):
        with open(file_name, mode='wb') as binary_file:
            pickle.dump(class_object, binary_file, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info('Serialized object to {} '.format(file_name))


def deserialize_class(file_name):
        logger.debug('Starting file {}  deserialization.'.format(file_name))
        return pickle.load(open(file_name, 'rb'))

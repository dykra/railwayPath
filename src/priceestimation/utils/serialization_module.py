import pickle
import logging
import os
from src.priceestimation.utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


_current_bucket_type_global = ""


def update_bucket_type(bucket_type):
    global _current_bucket_type_global
    _current_bucket_type_global = bucket_type


def serialize_class_pickle(file_name, class_object):
        with open(file_name, mode='wb') as binary_file:
            pickle.dump(class_object, binary_file, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info('Serialized object to {} '.format(file_name))


def deserialize_class_pickle(file_name):
        logger.debug('Starting file {}  deserialization.'.format(file_name))
        return pickle.load(open(file_name, 'rb'))


def serialization_object_decorate(
        serialize_function, deserialize_function):
    def serialization_with_arguments(func):
        def func_wrapper(*args, **kwargs):
            if os.path.exists(_current_bucket_type_global):
                return deserialize_function(file_name=_current_bucket_type_global)
            result = func(*args, **kwargs)
            serialize_function(_current_bucket_type_global, result)
            return result
        return func_wrapper
    return serialization_with_arguments

import pickle
import logging
import os
from src.parcels_valuation.utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def make_file_name(base_name, _limit_date, bucket='', extension='.h5'):
    return base_name + str(_limit_date) + '_' + bucket + extension


def serialization_object_decorate(
        serialize_function, deserialize_function):
    def serialization_with_arguments(func):
        def func_wrapper(*args, **kwargs):
            model_filename = kwargs["model_file_name"]
            if os.path.exists(model_filename):
                return deserialize_function(file_name=model_filename)
            result = func(*args, **kwargs)
            serialize_function(model_filename, result)
            return result

        return func_wrapper

    return serialization_with_arguments

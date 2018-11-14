import logging
import os
from utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def serialization_object_decorate(
        serialize_function, deserialize_function):
    def serialization_with_arguments(func):
        def func_wrapper(*args, **kwargs):
            model_filename = kwargs["model_file_name"]
            overwrite_model = kwargs["overwrite"]
            if os.path.exists(model_filename) and overwrite_model is False:
                return deserialize_function(file_name=model_filename)
            result = func(*args, **kwargs)
            serialize_function(model_filename, result)
            return result

        return func_wrapper

    return serialization_with_arguments

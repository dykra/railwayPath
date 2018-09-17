import pickle
import logging
import os
from src.priceestimation.utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def serialize_class_pickle(file_name, class_object):
        with open(file_name, mode='wb') as binary_file:
            pickle.dump(class_object, binary_file, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info('Serialized object to {} '.format(file_name))


def deserialize_class_pickle(file_name):
        logger.debug('Starting file {}  deserialization.'.format(file_name))
        return pickle.load(open(file_name, 'rb'))

#
# def deserialize_with_keras(file_name):
#         logger.debug('Starting file {}  deserialization.'.format(file_name))
#         return pickle.load(open(file_name, 'rb'))


def serialization_object_decorate(file_path, serialize_function, deserialize_function):
    def serialization_with_arguments(func):
        def func_wrapper(*args, **kwargs):
            logger.info('Wrapper')
            print(file_path)
            if os.path.exists(file_path):
                logger.debug('Loading file ' + file_path)
                return deserialize_function(file_name=file_path)
            result = func(*args, **kwargs)
            serialize_function(file_path, result)
            return result

        return func_wrapper
    return serialization_with_arguments


# @serialization_object_decorate
# def prepare_classification_model(data, target_column=target_column_name):
#     return ClassificationLogisticRegression(data, target_column)

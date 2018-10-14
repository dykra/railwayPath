import os.path
from sklearn import model_selection
import sys
import logging
from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.logger import create_loggers_helper
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from src.parcels_valuation.utils.serialization_module import *
from src.parcels_valuation.configuration.configuration_constants import target_column_name
from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.utils.serialization_module import serialization_object_decorate


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


class CalculateValue:
    def __init__(self, trained_model):
        self.model = trained_model
        self.target_column = trained_model.target_column

    def predict(self, data_to_predict):
        y = data_to_predict[self.model.target_column]
        X = data_to_predict[self.model.X_columns]
        y_predicted = self.model.model.predict(X)
        logger.info('Accuracy of logistic regression classifier on test set: {:.2f}'
                    .format(self.model.model.score(X, y)))
        return y_predicted


@serialization_object_decorate(serialize_function=serialize_class_pickle,
                               deserialize_function=deserialize_class_pickle
                               )
def get_model(query, model_file_name, target_column, database_handler):
    logger.info('Creation of model.')
    data_to_train_the_model = database_handler.execute_query(query)
    classification_regression_model = ClassificationLogisticRegression(data_to_train_the_model, target_column)
    logger.info('Model is trained.')
    return classification_regression_model


class ClassificationLogisticRegression:
    def __init__(self, input_data, target_column_name):
        self.data_final = input_data
        self.target_column = target_column_name
        self.y_column = [target_column_name]
        self.X_columns = [i for i in input_data if i not in self.y_column]
        self.model = self.logistic_regression()

    def logistic_regression(self):
        logistic_reg = LogisticRegression()
        logistic_reg.fit(self.data_final[self.X_columns], self.data_final[self.y_column].values.ravel())
        logger.debug('Logistic regression model is computed.')
        return logistic_reg

# TODO moze na to cross_validation_regression trzeba to przerobic? ? ?
    def cross_validation_regression(self):
        k_fold = model_selection.KFold(n_splits=10, random_state=7)
        model_cv = LogisticRegression()
        scoring = 'accuracy'
        results = model_selection.cross_val_score(model_cv,
                                                  self.data_final[self.X_columns],
                                                  self.data_final[self.y_column].values.ravel(),
                                                  cv=k_fold,
                                                  scoring=scoring)
        logger.info("10-fold cross validation average accuracy: %.3f" % (results.mean()))
        return model_cv

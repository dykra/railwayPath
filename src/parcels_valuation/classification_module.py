import logging
from utils.logger import create_loggers_helper
from sklearn.linear_model import LogisticRegression
# from sklearn.linear_model import LogisticRegressionCV as LogisticRegression
# from sklearn.neighbors import KNeighborsClassifier as LogisticRegression
# from sklearn.tree import DecisionTreeClassifier as LogisticRegression
from utils.serialization_module import serialization_object_decorate

from sklearn.externals import joblib


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def serialize_classification_model(file_name, model):
    joblib.dump(model, file_name)
    logger.info('Model serialized to {} '.format(file_name))


def deserialize_classification_model(file_name):
    logger.debug('Model {}  deserialization.'.format(file_name))
    return joblib.load(file_name)


class CalculateValue:
    def __init__(self, trained_model):
        self.model = trained_model
        self.target_column = trained_model.target_column

    def predict(self, data_to_predict):
        y = data_to_predict[self.model.target_column]
        X = data_to_predict[self.model.X_columns]
        y_predicted = self.model.model.predict(X)
        logger.info('Accuracy of logistic regression: {:.4f}'
                    .format(self.model.model.score(X, y)))
        return y_predicted


@serialization_object_decorate(serialize_function=serialize_classification_model,
                               deserialize_function=deserialize_classification_model,
                               )
def get_model(query, model_file_name, target_column, database_handler, overwrite=False):
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
        logistic_reg = LogisticRegression(solver='liblinear', multi_class='auto')
        logistic_reg.fit(self.data_final[self.X_columns], self.data_final[self.y_column].values.ravel())
        logger.debug('Logistic regression model is computed.')
        return logistic_reg

    def cross_validation_regression(self):
        model_cv = LogisticRegression(solver='liblinear', multi_class='auto')
        model_cv.fit(self.data_final[self.X_columns], self.data_final[self.y_column].values.ravel())
        return model_cv

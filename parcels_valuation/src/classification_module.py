import logging
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from utils.logger import create_loggers_helper
from utils.serialization_module import serialization_object_decorate


from sklearn.externals import joblib


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def save_classification_model(file_name, model):
    joblib.dump(model, file_name)
    logger.info('Model serialized to {} '.format(file_name))


def restore_classification_model(file_name):
    logger.debug('Model {}  deserialization.'.format(file_name))
    return joblib.load(file_name)


class CalculateValue:
    def __init__(self, trained_model):
        self.model = trained_model
        self.target_column = trained_model.target_column

    def predict(self, data_to_predict):
        y = data_to_predict[self.model.target_column]
        x = data_to_predict[self.model.X_columns]
        y_predicted = self.model.model.predict(x)
        logger.info('Accuracy of logistic regression: {:.4f}'
                    .format(self.model.model.score(x, y)))
        return y_predicted


@serialization_object_decorate(serialize_function=save_classification_model,
                               deserialize_function=restore_classification_model,
                               )
def get_model(query, model_file_name, target_column, database_handler, overwrite=False):
    logger.info('Creation of model.')
    data_to_train_the_model = database_handler.execute_query(query)
    classification_regression_model = ClassificationLogisticRegressionModel(data_to_train_the_model, target_column)
    logger.info('Model is trained.')
    return classification_regression_model


class ClassificationLogisticRegressionModel:
    def __init__(self, input_data, target_column_name):
        self.data = input_data
        self.target_column = target_column_name
        self.y_column = [target_column_name]
        self.X_columns = [i for i in input_data if i not in self.y_column]
        self.model = self.create_logistic_regression_model()

    def create_logistic_regression_model(self):
        logistic_reg = LogisticRegression(solver='liblinear', multi_class='auto')
        train_set, test_set = train_test_split(self.data, test_size=0.2)
        logistic_reg.fit(train_set[self.X_columns], train_set[self.y_column].values.ravel())

        y_test_set = test_set[self.target_column]
        x_test_set = test_set[self.X_columns]
        y_predicted = logistic_reg.predict(x_test_set)

        logger.info('Model accuracy: ' + str(accuracy_score(y_true=y_test_set, y_pred=y_predicted)))

        logger.debug('Logistic regression model is computed.')
        return logistic_reg

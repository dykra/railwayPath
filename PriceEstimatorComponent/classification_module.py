import os.path
from sklearn import model_selection
import sys
import logging

from PriceEstimatorComponent.database_handler import execute_sql_statement
from PriceEstimatorComponent.logger import create_loggers_helper
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from PriceEstimatorComponent.serialization import serialize_class, deserialize_class
sys.path.insert(0, './classification')

# https://towardsdatascience.com/train-test-split-and-cross-validation-in-python-80b61beca4b6
# https://towardsdatascience.com/building-a-logistic-regression-in-python-step-by-step-becd4d56c9c8


def create_loggers():
    logger1 = logging.getLogger(__name__)
    logger1.setLevel(logging.DEBUG)
    logger1 = create_loggers_helper(logger1)
    return logger1


logger = create_loggers()


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


# https://datascience.blog.wzb.eu/2016/08/12/a-tip-for-the-impatient-simple-caching-with-python-pickle-and-decorators/


def serialization_object_decorate(func, file_path="./index.pickle"):
    def func_wrapper(*args, **kwargs):
        logger.info('Wrapper')
        if os.path.exists(file_path):
            logger.debug('Loading file ' + file_path)
            return deserialize_class(file_name=file_path)
        result = func(*args, **kwargs)
        serialize_class(file_path, result)
        return result

    return func_wrapper


@serialization_object_decorate
def prepare_classification_model(data, target_column_name='Price_Group'):
    return ClassificationLogisticRegression(data, target_column_name)


def classification_regression():
    data_frame = execute_sql_statement(server=sys.argv[1], user_name=sys.argv[2], database_name=sys.argv[3],
                                       statement='select '
                                                 'Price_Group, '
                                                 'Residential,'
                                                 'Special_Purposes_Plan, '
                                                 'Agricultural, Commercial,  '
                                                 'Manufacturing, '
                                                 'Price_Per_Single_Area_Unit, '
                                                 'IMPROVE_Curr_Value, PARCEL_TYP, '
                                                 'LAND_Curr_Value, '
                                                 'PERIMETER,'
                                                 'PARCEL_TYP,'
                                                 'CENTER_X,'
                                                 'CENTER_Y,'
                                                 'CENTER_LAT,'
                                                 'CENTER_LON,'
                                                 'Parcel_Area,'
                                                 'LAND_Curr_Roll_Yr,'
                                                 'IMPROVE_Curr_Roll_YR,'
                                                 'BD_LINE_1_Yr_Built,'
                                                 'BD_LINE_1_Sq_Ft_of_Main_Improve,'
                                                 'City_int,'
                                                 'Current_improvement_base_value,'
                                                 'cluster_location,'
                                                 'cluster_type '
                                                 'FROM FILTERED_PARCEL'
                                       )
    train, test = train_test_split(data_frame, test_size=0.2)
    logger.debug('Data splited for training and test')
    model = prepare_classification_model(train, 'Price_Group')
    CalculateValue(model).predict(data_to_predict=test)
    logger.info('Prediction is done.')


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
        logger.debug('Logistic regression model is computed')
        return logistic_reg

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


if __name__ == '__main__':
    classification_regression()

from src.Utils.database_handler import execute_sql_statement
from src.Utils.logger import create_loggers_helper
import sys
import logging
import  pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import logging
import pickle
indexed_file = "./index.pickle"

# https://towardsdatascience.com/train-test-split-and-cross-validation-in-python-80b61beca4b6
# todo cross validation :)

def create_loggers():
    logger1 = logging.getLogger(__name__)
    logger1.setLevel(logging.INFO)
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
        # confusion_matrix = metrics.confusion_matrix(y, y_pred)
        # print(confusion_matrix)

# https://datascience.blog.wzb.eu/2016/08/12/a-tip-for-the-impatient-simple-caching-with-python-pickle-and-decorators/


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

# def label_race (row):
#    if row['LAND_Curr_Value'] <= 100090:
#       return 'small'
#    if row['LAND_Curr_Value'] <= 500090:
#        return 'medium'
#    return 'large'


# TODO sprawdzić czy nie lepiej wyznaczać kubełek z 1) cena zadeklarowana 2) cena za jaka sprzedano
if __name__ == '__main__':
    # TODO popatrzec na kolumny i wyciagnac ich maksymalnie duzo -> ewentualnie od nowa przeleciec skryptem i zobaczyc czy te przekształcenia wystarzaja zeby wziac wszystkie kolumny z wartosciami INT
    data_frame = execute_sql_statement(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                                 'select Price_Group, Residential,Special_Purposes_Plan, Agricultural, Commercial,  '
                                 'Manufacturing, Price_Per_Single_Area_Unit, IMPROVE_Curr_Value, PARCEL_TYP, '
                                 'LAND_Curr_Value, PERIMETER, PARCEL_TYP , CENTER_X ,CENTER_Y , CENTER_LAT, '
                                 'CENTER_LON , Parcel_Area, LAND_Curr_Roll_Yr, IMPROVE_Curr_Roll_YR, BD_LINE_1_Yr_Built,'
                                 ' BD_LINE_1_Sq_Ft_of_Main_Improve, City_int, Current_improvement_base_value, cluster_location, cluster_type'
                                 ' FROM FILTERED_PARCEL')
    # TODO przetrenować inne te metody z tego tutoriala ktory był
    # data_frame = data_frame.select_dtypes(include=['number'])
    # data_frame['Price_Group'] = data_frame.apply(lambda row: label_race(row), axis=1)
    train, test = train_test_split(data_frame, test_size=0.2)
    model = ClassificationLogisticRegression(train, 'Price_Group')
    classificaton = CalculateValue(model)
    classificaton.predict(data_to_predict=test)


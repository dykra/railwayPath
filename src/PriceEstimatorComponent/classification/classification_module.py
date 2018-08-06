from src.Utils.DatabaseHandler import DatabaseHandler
from src.Utils.logger import create_loggers_helper
import pandas as pd
import sys
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split

# import matplotlib.pyplot as plt
#
#
# import seaborn as sns
# sns.set(style="white")
# sns.set(style="whitegrid", color_codes=True)

# show_statistics(data)

#
# def show_statistics(data):
#     sns.countplot(x='Price_Group', data=data, palette='hls')
#     plt.show()
#     plt.savefig('count_plot')


def create_loggers():
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger = create_loggers_helper(logger)
    return logger


# logger = create_loggers()
# logger.debug("I am in estimation_time function.")


class CalculateValue:
    def __init__(self, trained_model):
        self.model = trained_model
        self.target_column = trained_model.target_column

    def predict(self, data_to_predict):
        y = data_to_predict[self.model.target_column]
        X = data_to_predict[self.model.X_columns]
        y_pred = self.model.model.predict(X)

        print(y_pred)
        print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(self.model.model.score(X, y)))
        confusion_matrix = metrics.confusion_matrix(y, y_pred)
        print(confusion_matrix)


# TODO decorator with pickle module
class ClassificationLogisticRegression:
    def __init__(self, input_data, target_column_name, step_size=2000):
        self.data_final = input_data
        self.target_column = target_column_name
        self.y_column = [target_column_name]
        self.X_columns = [i for i in input_data if i not in self.y_column]
        # self.h = step_size   # step size in the mesh
        self.model = self.logistic_regression()

    def logistic_regression(self):
        logreg = LogisticRegression()
        logreg.fit(self.data_final[self.X_columns], self.data_final[self.y_column].values.ravel())
        return logreg


def execute_sql_statement(server, user, password, database_name, statement):
    database_handler = DatabaseHandler(server, user, password, database_name)
    # print(database_handler.execute_statement(statement))
    return pd.read_sql(statement, database_handler.conn)
    #    database_handler.execute_statement(statement)

#TODO  zaleznosc danych od wyniku (wykresy) : cena , lattitude i longitude :)

if __name__ == '__main__':
# TODO popatrzec na kolumny i wyciagnac ich maksymalnie duzo -> ewentualnie od nowa przeleciec skryptem i zobaczyc czy te przekształcenia wystarzaja zeby wziac wszystkie kolumny z wartosciami INT
# TODO przetrenować inne te metody z tego tutoriala ktory był
    data = execute_sql_statement(sys.argv[1], sys.argv[2] , sys.argv[3] , sys.argv[4] ,
                                 'select Price_Group, Residential,Special_Purposes_Plan, Agricultural, Commercial,  '
                                 'Manufacturing, Price_Per_Single_Area_Unit, IMPROVE_Curr_Value, PARCEL_TYP, '
                                 'LAND_Curr_Value, PERIMETER, PARCEL_TYP , CENTER_X ,CENTER_Y , CENTER_LAT, '
                                 'CENTER_LON , Parcel_Area, LAND_Curr_Roll_Yr, IMPROVE_Curr_Roll_YR, BD_LINE_1_Yr_Built,'
                                 ' BD_LINE_1_Sq_Ft_of_Main_Improve, City_int'
                                                                                 ' FROM FILTERED_PARCEL')

    train, test = train_test_split(data, test_size=0.2)
    model = ClassificationLogisticRegression(train, 'Price_Group')
    classificaton = CalculateValue(model)
    classificaton.predict(data_to_predict=test)
    # show_statistics(data)
    # print(data)
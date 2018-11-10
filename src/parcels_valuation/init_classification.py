import csv

from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.serialization_module import *
from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.classification_module import CalculateValue, get_model, ClassificationLogisticRegression
from sklearn.model_selection import train_test_split

query_step_iterate = 200000


def classification_regression_with_test_set():
    database_handler = DatabaseHandler()
    query = "EXEC dbo.GetDateToTrainClassificationModel @LimitDate = {}, @ExcludedList ='{}'".format(limit_date,
                                                                                                     excluded_values)
    data = database_handler.execute_query(query)
    train, test = train_test_split(data, test_size=0.3)
    model = ClassificationLogisticRegression(input_data=train, target_column_name=target_column_name)
    prediction = CalculateValue(model).predict(data_to_predict=test)
    from sklearn.metrics import accuracy_score
    print(accuracy_score(y_true=test[target_column_name], y_pred=prediction))
    database_handler.close_connection()
    for predictionItem, realItem in zip(prediction, test[target_column_name]):
        if predictionItem != realItem:
            print(predictionItem)
            print(realItem)
            print("\n")
    # print(prediction)
    # print(test[target_column_name])


def classification_regression():
    database_handler = DatabaseHandler()
    model_file_name = make_file_name(base_name=path_to_trained_models + "classification_",
                                     _limit_date=limit_date,
                                     extension='.sav')

    model = get_model("EXEC dbo.GetDateToTrainClassificationModel @LimitDate = {}, @ExcludedList ='{}'"
                      .format(limit_date, excluded_values),
                      target_column=target_column_name,
                      model_file_name=model_file_name,
                      database_handler=database_handler)

    min_max_object_id = \
        database_handler.execute_query("EXEC dbo.GetMinimumAndMaxumimObjectID @LimitDate = {}, @ExcludedList ='{}'"
                                       .format(limit_date, excluded_values))
    min_object_id = min_max_object_id.iloc[0]["MinimumObjectID"]
    max_object_id = min_max_object_id.iloc[0]["MaximumObjectID"]
    try:
        with open(make_file_name(file_name_predicted_bucket_values, extension='.csv'), mode='a') as estimated_bucket_values:
            estimated_bucket_writer = csv.writer(estimated_bucket_values,
                                                 delimiter=',',
                                                 quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)

            tmp_min = min_object_id
            while tmp_min < max_object_id:
                if tmp_min + query_step_iterate < max_object_id:
                    tmp_max = tmp_min + query_step_iterate
                else:
                    tmp_max = max_object_id
                df_parcels_to_estimate_price_group = database_handler.execute_query(
                    "EXEC dbo.GetDataToParcelClassification "
                    "@LimitDate = {}, @ExcludedList='{}', @ObjectIdMin = {}, @ObjectIdMax = {}"
                    .format(limit_date, excluded_values, tmp_min, tmp_max))
                prediction = CalculateValue(model).predict(data_to_predict=df_parcels_to_estimate_price_group)
                print(prediction)
                for (prediction_value, object_id) in zip(prediction, df_parcels_to_estimate_price_group['OBJECTID']):
                    # query = ("EXEC dbo.UpdateEstimatedPriceLevelGroup "
                    #          "@NEW_Estimated_Price_Group = {}, @ObjectID = {} "
                    #          .format(prediction_value, object_id))
                    # database_handler.cursor.execute(query)
                    # database_handler.conn.commit()

                    estimated_bucket_writer.writerow([object_id, prediction_value])

                tmp_min = tmp_max
    finally:
        database_handler.close_connection()
    logger.info('Classification prediction is done.')


if __name__ == '__main__':
    classification_regression()
    # classification_regression_with_test_set()

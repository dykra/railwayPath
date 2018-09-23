import argparse
from src.priceestimation.configuration_constants import *
from src.priceestimation.database_connection_constants import *
from src.priceestimation.price_estimator_model_preparator import generate_file_name_with_price_limit, update_bucket_type, prepare_price_estimator_model
from src.priceestimation.utils.database_handler import DatabaseHandler

#
# def parse_args():
#     parser = argparse.ArgumentParser(description='Program to predict lands prices.')
#     parser.add_argument('--database', help='Database name.')
#     parser.add_argument('--server', help='Server address.')
#     parser.add_argument('--database_user', help='Database user name.')
#     return parser.parse_args()


def main():
    # args = parse_args()
    database_handler = DatabaseHandler(server=server, user_name=user_name, database_name=database_name)
    for set_type in classification_buckets:
        print('Set type ' + set_type)
        update_bucket_type(bucket_type=generate_file_name_with_price_limit(base_name=prediction_prices_model_file_path,
                                                                           bucket_type=set_type))
        model = prepare_price_estimator_model(execute_view_query="EXEC dbo.getTrainingDataPriceEstimation "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                              .format(date_limit,
                                                      set_type,
                                                      excluded_values),
                                              database_handler=database_handler,
                                              bucket_type=set_type)
        df_values_to_predict = database_handler.execute_query("EXEC dbo.getDataForPriceCalculation "
                                                              "@LimitDate = {}, "
                                                              "@BucketType={}, "
                                                              "@ExcludedList='{}'"
                                                              .format(date_limit, set_type, excluded_values))
        prediction = model.predict(df_values_to_predict)
        for (prediction_value, object_id) in zip(prediction, df_values_to_predict['OBJECTID']):
            database_handler.execute_query("EXEC dbo.UpdateParcelVectors @L1_Sale_Amount = {} @ObjectID = {} ".
                                           format(prediction_value, object_id))
    database_handler.close_connection()


if __name__ == '__main__':
    main()

from src.priceestimation.constants.configuration_constants import *
from src.priceestimation.constants.database_connection_constants import *
from src.priceestimation.model_to_parcels_valuation import generate_file_name_with_price_limit, update_bucket_type, prepare_price_estimator_model
from src.priceestimation.utils.database_handler import DatabaseHandler


def main():
    database_handler = DatabaseHandler(server_name=server_name, database_name=database_name, user_name=user_name)
    for bucket in classification_buckets:
        update_bucket_type(bucket_type=generate_file_name_with_price_limit(base_name=prediction_prices_model_file_path,
                                                                           limit_date=date_limit,
                                                                           bucket_type=bucket))
        model = prepare_price_estimator_model(execute_view_query="EXEC dbo.getTrainingDataPriceEstimation "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                              .format(date_limit,
                                                      bucket,
                                                      excluded_values),
                                              database_handler=database_handler,
                                              bucket_type=bucket)
        df_parcels_to_valuation = database_handler.execute_query("EXEC dbo.getDataForPriceCalculation "
                                                              "@LimitDate = {}, "
                                                              "@BucketType={}, "
                                                              "@ExcludedList='{}'"
                                                              .format(date_limit, bucket, excluded_values))
        prediction = model.predict(df_parcels_to_valuation)
        for (prediction_value, object_id) in zip(prediction, df_parcels_to_valuation['OBJECTID']):
            database_handler.execute_query("EXEC dbo.UpdateParcelVectors @L1_Sale_Amount = {} @ObjectID = {} ".
                                           format(prediction_value, object_id))
    database_handler.close_connection()


if __name__ == '__main__':
    main()

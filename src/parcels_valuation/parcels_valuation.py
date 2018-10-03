from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.model import make_file_name, set_model_filename, \
    prepare_price_estimator_model
from src.parcels_valuation.utils.database_handler import DatabaseHandler


def main():
    database_handler = DatabaseHandler()
    for bucket in classification_buckets:
        model_filename = make_file_name(base_name=prediction_prices_model_file_path,
                                        limit_date=date_limit,
                                        bucket_type=bucket)
        set_model_filename(_model_filename=model_filename)
        model = prepare_price_estimator_model(execute_view_query="EXEC dbo.GetDateToTrainModel "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                              .format(date_limit,
                                                      bucket,
                                                      excluded_values),
                                              database_handler=database_handler,
                                              bucket_type=bucket)
        df_parcels_to_valuation = database_handler.execute_query("EXEC dbo.GetDataToParcelsValuation "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                                                 .format(date_limit, bucket, excluded_values))
        prediction = model.predict(df_parcels_to_valuation)
        for (prediction_value, object_id) in zip(prediction, df_parcels_to_valuation['OBJECTID']):
            database_handler.execute_query("EXEC dbo.UpdateEstimated_Amount @NEW_Estimated_Amount = {} @ObjectID = {} ".
                                           format(prediction_value, object_id))
    database_handler.close_connection()


if __name__ == '__main__':
    main()

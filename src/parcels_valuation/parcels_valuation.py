from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.model import make_file_name, get_model
from src.parcels_valuation.utils.database_handler import DatabaseHandler


def main():
    database_handler = DatabaseHandler()
    for bucket in classification_buckets:
        model_filename = make_file_name(base_name=path_to_trained_models,
                                        _limit_date=limit_date,
                                        bucket=bucket)
        model = get_model("EXEC dbo.GetDateToTrainModel "
                          "@LimitDate = {}, "
                          "@BucketType={}, "
                          "@ExcludedList='{}'"
                          .format(limit_date,
                                  bucket,
                                  excluded_values),
                          database_handler,
                          model_file_name=model_filename)
        df_parcels_to_valuation = database_handler.execute_query("EXEC dbo.GetDataToParcelsValuation "
                                                                 "@LimitDate = {}, "
                                                                 "@BucketType={}, "
                                                                 "@ExcludedList='{}'"
                                                                 .format(limit_date, bucket, excluded_values))
        prediction = model.predict(df_parcels_to_valuation)
        for (prediction_value, object_id) in zip(prediction, df_parcels_to_valuation['OBJECTID']):
            database_handler.execute_query("EXEC dbo.UpdateEstimated_Amount @NEW_Estimated_Amount = {} @ObjectID = {} ".
                                           format(prediction_value, object_id))
    database_handler.close_connection()


if __name__ == '__main__':
    main()

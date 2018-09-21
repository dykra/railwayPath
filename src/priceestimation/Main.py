from src.priceestimation.configuration_constants import *
from src.priceestimation.database_connection_constants import *
from src.priceestimation.price_estimator_model_preparator import generate_file_name_with_price_limit, update_bucket_type, prepare_price_estimator_model
from src.priceestimation.utils.database_handler import DatabaseHandler

# TODO - argparse
if __name__ == '__main__':
    database_handler = DatabaseHandler(server=server, user_name=user_name, database_name=database_name)
    for set_type in classification_buckets:
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
        # prediction = model.predict(x.values)
        # print('First prediction:', prediction[0])
        # TODO - save predictions to the database (in other program)
        # TODO - predict for all rows from database (in other program)
    database_handler.close_connection()

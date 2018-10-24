import csv
import os

from keras.engine.saving import load_model

from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.file_names_builder import get_model_filename
from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.logger import create_loggers_helper
import logging


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def keras_load_model(file_name):
    if os.path.exists(get_model_filename()):
        logger.info('Loading model from {}.'.format(file_name))
        return load_model(file_name)
    else:
        logger.error('The model can not be found. Firstly run neural_network_model_trainer.py')
        return


def main():
    database_handler = DatabaseHandler()
    try:
        query = ''
        with open('estimated_prices.csv', mode='w') as estimated_prices_file:
            estimated_prices_writer = csv.writer(estimated_prices_file, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)

            # examples: employee_writer.writerow(['John Smith', 'Accounting', 'November'])
            # employee_writer.writerow(['Erica Meyers', 'IT', 'March'])


        for bucket in classification_buckets:
            model_filename = get_model_filename()

            model = keras_load_model(model_filename)

            df_parcels_to_valuation = database_handler.execute_query("EXEC dbo.GetDataToParcelsValuation "
                                                                     "@LimitDate = {}, "
                                                                     "@BucketType={}, "
                                                                     "@ExcludedList='{}'"
                                                                     .format(limit_date, bucket, excluded_values))
            x = df_parcels_to_valuation.iloc[:, 1:71]
            prediction = model.predict(x)
            print(prediction)

            for (prediction_value, object_id) in zip(prediction, df_parcels_to_valuation['OBJECTID']):
                query += "EXEC dbo.UpdateEstimated_Amount @NEW_Estimated_Amount = {}, @ObjectID = {}; "\
                    .format(prediction_value[0], object_id)
        path = './../resources/EstimatedAmountQuery.txt'
        file_with_query = open(path, 'w')
        file_with_query.write(query)
        file_with_query.close()
        #database_handler.execute_query(query)

    finally:
        database_handler.close_connection()


if __name__ == '__main__':
    main()

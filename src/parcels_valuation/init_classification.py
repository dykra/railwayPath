from src.parcels_valuation.utils.database_handler import DatabaseHandler
from src.parcels_valuation.utils.serialization_module import *
from src.parcels_valuation.configuration.configuration_constants import *
from src.parcels_valuation.classification_module import CalculateValue, get_model


def classification_regression():
    # TODO make it for portions, dla procedury po obkectID jakos mozna srotwac numerkami;
    # albo jest jakis sprytny sposob na zwracanie czesci
    database_handler = DatabaseHandler()
    model_file_name = make_file_name(base_name=path_to_trained_models + "classification_", _limit_date=limit_date,
                                     extension='.pickle')

    model = get_model("EXEC dbo.GetDateToTrainClassificationModel @LimitDate = {}, @ExcludedList ='{}'"
                      .format(limit_date, excluded_values),
                      target_column=target_column_name,
                      model_file_name=model_file_name,
                      database_handler=database_handler)

    df_parcels_to_estimate_price_group = database_handler.execute_query("EXEC dbo.GetDataToParcelClassification "
                                                                        "@LimitDate = {}, "
                                                                        "@ExcludedList='{}'"
                                                                        .format(limit_date, excluded_values))

    prediction = CalculateValue(model).predict(data_to_predict=df_parcels_to_estimate_price_group)
    for (prediction_value, object_id) in zip(prediction, df_parcels_to_estimate_price_group['OBJECTID']):
        print(prediction_value)
        print(object_id)
        query = ("EXEC dbo.UpdateEstimatedPriceLevelGroup "
                                       "@NEW_Estimated_Price_Group = {}, @ObjectID = {} "
                                       .format(prediction_value, object_id))
        # database_handler.execute_query("EXEC dbo.UpdateEstimatedPriceLevelGroup "
        #                                "@NEW_Estimated_Price_Group = {}, @ObjectID = {} "
        #                                .format(prediction_value, object_id))
        database_handler.cursor.execute(query)
        database_handler.conn.commit()
        break
    database_handler.close_connection()
    logger.info('Classification prediction is done.')


if __name__ == '__main__':
    classification_regression()

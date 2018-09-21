"""
    Date to separate new data for learning the model
    provided in format 'YYYYMMDD'.
"""
date_limit = 20150000

"""
    Price values to exclude from training the model.
"""
excluded_values = '0;9;999999999'

"""
    Neural Network model parameters
"""
seed = 7
epochs_value = 200
validation_split_value = 0.1
verbose_value = 2

"""
    Names of buckets to divide the data for few models. 
    Same names are used in destination table.
"""
classification_buckets = ['cheap', 'medium', 'expensive']

"""
    Paths where to place the model and best values during model training.
"""
weights_file_path = './../resources/init_weights.hdf5'
prediction_prices_model_file_path = './trained_models/'
checkpoint_file_path = './../resources/'


""" Price classification module configuration constants """
target_column_name = 'Price_Group_int'

"""
    Lower limit date to filter data in order to train the model
    provided in format 'YYYYMMDD'.
"""
limit_date = 20150000

"""
    Price values excluded from training the model.
"""
excluded_values = '0;9;999999999'


"""
    Names of buckets to divide the data. 
    Same names are used in destination table.
"""
classification_buckets = ['cheap', 'medium', 'expensive']


"""
    Neural Network model parameters
"""
seed = 7
epochs_value = 200
validation_split_value = 0.1
verbose_value = 2

"""
   Paths:
    - initial weights for neural network before start training the model
    - best results from one training iteration
"""
weights_file_path = './../resources/init_weights.hdf5'
checkpoint_file_path = './../resources/'

"""
   Paths:
    - path for trained models for both: classification and price estimation
"""
path_to_trained_models = './trained_models/'


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
    Neural Network model parameters
"""
seed = 7
epochs_value = 200
validation_split_value = 0.1
verbose_value = 2

"""
    Names of buckets to divide the data. 
    Same names are used in destination table.
"""
classification_buckets = ['cheap', 'medium', 'expensive']

"""
   Paths:
    - initial weights for neural network before start training the model
    - trained models
    - best results from one training iteration
"""
weights_file_path = './../resources/init_weights.hdf5'
path_to_trained_models = './trained_models/'
checkpoint_file_path = './../resources/'


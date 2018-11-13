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
epochs_value = 10
validation_split_value = 0.1
verbose_value = 2

"""
    Names of buckets to divide the data. 
    Same names are used in destination table.
"""
classification_buckets = ['cheap', 'medium', 'expensive']

"""
    Name of bucket currently using to train neural network model.
"""
current_bucket = 'expensive' # 'cheap'

"""
   Paths to:
    - initial weights for neural network before start training the model
    - folder to save trained models files
    - folder to save files with best results from one training iteration
    - names convention for trained models and checkpoints files
"""
weights_file_path = './../resources/init_weights.hdf5'
model_target_folder = './trained_models/withoutPrices'
# model_target_folder = './parcels_valuation/trained_models/'
checkpoint_file_target_folder = './../resources/best_results/checkpoint_'
file_names_convention = str(limit_date) + '_' + current_bucket

"""
  Variable to set if the model will be training using price parameters or without it. 
  Depends on it, program will call different procedure, which return data with different amount of columns. 
"""
train_model_with_price_parameters = False

"""
  Variable to set if overwrite file with neural network model or not. 
  Warning! If set to True, previous model would be lost. 
"""
model_overwrite = True # False
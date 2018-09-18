date_limit = 20150000
excluded_values = [0, 9, 999999999]
seed = 7
classification_buckets = ['cheap', 'medium', 'expensive']

weights_file_path = './../resources/init_weights.hdf5'
prediction_prices_model_file_path = './trained_models/'
checkpoint_file_path = './../resources/500tys_1mln-test.hdf5'

# Neural netowork model parameters
epochs_value = 200
validation_split_value = 0.1
verbose_value = 2

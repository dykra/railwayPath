from src.parcels_valuation.configuration.configuration_constants import model_target_folder, file_names_convention, \
    checkpoint_file_target_folder, limit_date


def get_model_filename():
    return model_target_folder + file_names_convention + '.h5'


def get_model_filename_b(bucket):
    return model_target_folder + str(limit_date) + '_' + bucket + '.h5'


def get_checkpoints_filename():
    return checkpoint_file_target_folder + file_names_convention + '.hdf5'

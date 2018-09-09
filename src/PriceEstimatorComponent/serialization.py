import pickle


def serialize_class(file_name, class_object):
        with open(file_name, mode='wb') as binary_file:
            pickle.dump(class_object, binary_file, protocol=pickle.HIGHEST_PROTOCOL)


def deserialize_class(file_name):
        return pickle.load(open(file_name, 'rb'))

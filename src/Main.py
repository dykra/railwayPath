
import sys
import pyodbc

import pandas as pd
import tensorflow as tf
import tensorflow.python # import pywrap_tensorflow
from keras.models import Sequential
from keras.layers import Dense
import numpy

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import matplotlib.pyplot as plt

import pickle

# --reading arguments
from keras.wrappers.scikit_learn import KerasRegressor


def baseline_model():
    model = Sequential()
    model.add(Dense(70, input_dim=70, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def main():

    #mode = ''

    argv = sys.argv

    print(argv[1])
    arg = argv[1]
    if arg == 'help':
        print('Main.py -mode 1 (connect to database) or Main.py -mode 2 (read from csv)')
        sys.exit()
    elif arg == '1':
        mode = 1
    elif arg == '2':
        mode = 2
    else:
        print('No such mode')
        sys.exit(2)

    print('Chosen mode is: ', mode)

    # you have to enable TCP/IP connection to SQL Server in SQL Server Configuration Manager
    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=DESKTOP-C1V4R2D;"
                      "Database=LosAngelesCounty;"
                      "Trusted_Connection=yes;")


    # ---------     Load data to DataFrame
    if mode == 1:
        df = pd.read_sql_query('select * from PARCEL_DATA_SET', cnxn)
    elif mode == 2:
        file = 'resources/Lands_Vectors.csv'
        df = pd.read_csv(file, delimiter=',')

    print('---Data loaded---')

    # split into X set and Y set było 68
    X = df.iloc[:, 1:71]
    Y = df.iloc[:, 71]
    ## 52
    print(X)
    print('-------')
    print(Y)

    # ---------   Define model
    # sequence of layers
    #  we will use a fully-connected network structure with three layers.
    #
    # Fully connected layers are defined using the Dense class

    # We can specify the number of neurons in the layer as the first argument,
    #  the initialization method as the second argument as init and specify
    # the activation function using the activation argument.


    print('Ok-1')
    # fix random seed for reproducibility
    seed = 2**32 - 29638824
    numpy.random.seed(seed)
    # evaluate model with standardized dataset
    estimator = KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=1, verbose=0)
    print('Ok-2')

    kfold = KFold(n_splits=2, random_state=seed)
    print('Ok-3')

    results = cross_val_score(estimator, X.values, Y.values, cv=kfold, n_jobs=1)
    print('Ok-4')
    print("Accuracy: %0.2f (+/- %0.2f)" % (results.mean(), results.std()*2))

    # Save to file in the current working directory
    pkl_filename = "pickle_model.pkl"
    with open(pkl_filename, 'wb') as file:
        pickle.dump(results, file)

    # Load from file
    with open(pkl_filename, 'rb') as file:
        pickle_model = pickle.load(file)

    # Calculate the accuracy score and predict target values
    score = pickle_model.score(X.values, Y.values)

    print("Test score: {0:.2f} %".format(100 * score))
    Ypredict = pickle_model.predict(X.values)
    print('Ok-5')


    # cross_val_predict returns an array of the same size as `y` where each entry
    # is a prediction obtained by cross validation:






    # fig, ax = plt.subplots()
    # ax.scatter(Y.values, results, edgecolors=(0, 0, 0))
    # ax.plot([Y.values.min(), Y.values.max()], [Y.values.min(), Y.values.max()], 'k--', lw=4)
    # ax.set_xlabel('Measured')
    # ax.set_ylabel('Predicted')
    # plt.show()
    #
    #

    # serialize model to JSON
    # model_json = results.to_json()
    # with open("model.json", "w") as json_file:
    #     json_file.write(model_json)
    # # serialize weights to HDF5
    # model.save_weights("model.h5")
    # print("Saved model to disk")
    #
    # # later...
    #
    # # load json and create model
    # json_file = open('model.json', 'r')
    # loaded_model_json = json_file.read()
    # json_file.close()
    # loaded_model = model_from_json(loaded_model_json)
    # # load weights into new model
    # loaded_model.load_weights("model.h5")
    # print("Loaded model from disk")
    #
    # # evaluate loaded model on test data
    # loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    # score = loaded_model.evaluate(X, Y, verbose=0)
    # print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))
    #


if __name__ == '__main__':
    main()
import numpy as np
import matplotlib.pyplot as plt
from keras.utils import np_utils
from alexnet import AlexNet
import plyvel

def train(db, keys, avg):
    m = len(keys)
    # 19 epochs
    iterations = 140000
    batch_size = 64
    stream_size = batch_size * 150 # ~10K images loaded at a time

    model = AlexNet()

    for i in range(0, m, stream_size):
        X_batch, Y_batch = get_data(db, keys[i:(i+stream_size)], avg)
        model.fit(X_batch, Y_batch, batch_size=batch_size, nb_epoch=1, verbose=1)

    # model.fit(X_train, Y_train,
    #       batch_size=64, nb_epoch=4700, verbose=1,
    #       validation_data=(X_test, Y_test))
    # max_iter = #epochs * (training set/training_batch_size) 

    return model


def get_data(dbpath, keys):
    X_train = np.array([])
    Y_train = np.array([])

    for key in keys:
        datum = caffe_pb2.Datum.FromString(db.get(key))
        img = caffe.io.datum_to_array(datum)
        # img.shape = 3x210x280
        img = img.reshape(1, 3*210*280) / 255
        img = np.subtract(img, avg);
        X_train = np.concatenate((X_train, img))

        affordances = [i for i in datum.float_data]
        affordances = M = np.array(affordances)
        affordances = affordances.reshape(1, 14)
        Y_train = np.concatenate((Y_train, affordances))

    # resize 3x210x280
    # subtract mean
    # crop = 0, mirror = false
    # shuffle

    X_train = X_train.astype('float32')
    Y_train = Y_train.astype('float32')
    return X_train, Y_train


def calc_average(db, keys):
    avg = np.zeros((3, 210, 280))
    n = 0

    for key in keys:
        datum = caffe_pb2.Datum.FromString(db.get(key))
        img = caffe.io.datum_to_array(datum)
        
        avg = np.add(avg*n, img) / (n+1)
        n = n+1

    avg = avg.reshape(1, 3*210*280) / 255
    return avg


if __name__ == "__main__":
    dbpath = '../TORCS_Training_1F/'
    db = plyvel.DB(dbpath)
    keys = []
    for key, value in db:
        keys.append(key)

    avg = calc_average(db, keys)
    model = train(db, keys, avg)

    model.save('deepdriving_model.h5')
    model.save_weights('deepdriving_weights.h5')
    with open('deepdriving_model.json', 'w') as f:
        f.write(model.to_json())

    db.close()



from train_combined import *

# nohup python evaluate.py &
# ps -ef | grep evaluate.py
# tail -f nohup.out
# kill UID


def test_data(db, keys, avg):
    m = len(keys)
    Y = np.empty((m, 14))
    Y[:] = db[:, 1:]

    # for i, key in enumerate(keys):
    #     j = int(key[-12:-4])
    #     affordances = db[j - 1]
    #     affordances = scale_output(affordances)

    mean = Y.mean(axis=0)
    maxx = np.amax(Y, axis=0)
    minn = np.amin(Y, axis=0)
    std = np.std(Y, axis=0)
    return mean[display_idx], maxx[display_idx], minn[display_idx], std[display_idx]


if __name__ == "__main__":
    dbpath = '/home/lkara/deepdrive/train_images/'
    keys = glob(dbpath + '*.jpg')
    keys.sort()
    db = np.load(dbpath + 'affordances.npy')
    db = db.astype('float32')

    avg = load_average()
    # avg.shape = 210x280x3
    if not same_size:
        avg = cv2.resize(avg, (227, 227))

    s1, s2, s3, s4 = test_data(db, keys, avg)
    print('Mean: ' + str(s1))
    print('Std: ' + str(s4))
    print('Max: ' + str(s2))
    print('Min: ' + str(s3))
    print("Time taken is %s seconds " % (time() - start_time))

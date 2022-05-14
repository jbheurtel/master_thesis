import numpy as np

y_predicted = np.array([1, 1, 0, 0, 1])
y_true = np.array([0.3, 0.7, 1, 0, 0.5])


def mae(y_true, y_predicted):
    total_error = 0
    for yt, yp in zip(y_true, y_predicted):
        total_error += abs(yt - yp)
    print("Total error: " + str(total_error))
    mae = total_error / len(y_true)
    print("MAE", mae)
    return mae

mae(y_true, y_predicted)
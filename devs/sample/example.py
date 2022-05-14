# This program classifies images

# set up env
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
import numpy as np

import matplotlib.pyplot as plt

from sample.t_funcs import t_cifar10

plt.style.use('fivethirtyeight')

path = r"/Users/jbheurtel/Desktop/S3/Thesis/TestCode/cifar-10-batches-py"
(x_train, y_train), (x_test, y_test) =t_cifar10(path)

# what type of data?

print(type(x_train))
print(type(y_train))
print(type(x_test))
print(type(y_test))

# what shape of data?
print('x_train shape:', x_train.shape)
print('y_train shape:', y_train.shape)
print('x_test shape:', x_test.shape)
print('y_test shape:', y_test.shape)

# take a look at the first image as an array
index = 1
print(x_train[index])

# take a look at the first image as a picture
img = plt.imshow(x_train[index])

# Get the image label -> number 6 corresponds to 'frog'
print('the image label is: ', y_train[index])

# Get the image classification
classification = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
# Print the image class
print('The image class is: ', classification[y_train[index][0]])

# Convert the labels into a set of 10 numbers to input into the neural network
y_train_one_hot = to_categorical(y_train)
y_test_one_hot = to_categorical(y_test)

# Print the new labels
print(y_train_one_hot)

# Print the new label of the image/picture above
print('The one hot label is: ', y_train_one_hot[index])

# Normalise the pixels to be values between 0 and 1.
x_train = x_train / 255
x_test = x_test / 255

# THE MODEL ARCHITECTURE
# TODO: Review wtf is going on here

# Create the models architecture
model = Sequential()

model.add(Conv2D(32, (5, 5), activation='relu', input_shape=(32, 32, 3)))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Conv2D(32, (5, 5), activation='relu', input_shape=(32, 32, 3)))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Flatten())
model.add(Dense(1000, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(500, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(250, activation='relu'))
model.add(Dense(10, activation='softmax'))

# MODEL TRAINING AND FITTING
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

hist = model.fit(x_train, y_train_one_hot,
                 batch_size=256,
                 epochs=10,
                 validation_split=0.2)

result = model.evaluate(x_test, y_test_one_hot)[1]
print('the model is accurate to: ' + str(round(result,4)*100) + "%")

plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

# Visualise the model's loss
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

# TODO: what are the concepts of "loss" and "accuracy"?

new_img = plt.imread(r"/Users/jbheurtel/Desktop/S3/Thesis/TestCode/cat_2.jpg")
img = plt.imshow(new_img)

# resize the image
from skimage.transform import resize
resized_image = resize(new_img, (32, 32, 3))
img = plt.imshow(resized_image)

# Get the models preditions
predictions = model.predict(np.array([resized_image]))

import pandas as pd

a = pd.DataFrame(list(predictions[0]), columns=["prob"])
b = pd.DataFrame(classification, columns=["class"])
c = a.merge(b, left_index=True, right_index=True)
c = c.set_index("class").sort_values("prob", ascending=False)
c = c.iloc[:4,:]
print(c)

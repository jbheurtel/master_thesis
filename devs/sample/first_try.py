import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.utils import to_categorical
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from keras.models import Sequential
import os
from sklearn.utils import shuffle

train_root = r"/Users/jbheurtel/Desktop/S3/Thesis/Data/archive/train_another"
path_train_dmg = os.path.join(train_root, "damage")
path_train_ndmg = os.path.join(train_root, "no_damage")

test_root = r"/Users/jbheurtel/Desktop/S3/Thesis/Data/archive/test_another"
path_test_dmg = os.path.join(train_root, "damage")
path_test_ndmg = os.path.join(train_root, "no_damage")


# Train Data - Damaged
all_img_names = os.listdir(path_train_dmg)
x_train_dmg = list()

count = 0
for i in all_img_names:
    pic_path = os.path.join(path_train_dmg, i)
    img = plt.imread(pic_path)
    x_train_dmg.append(img)

y_train_dmg = [1]*len(x_train_dmg)

# Train Data - Not Damaged
all_img_names = os.listdir(path_train_ndmg)
x_train_ndmg = list()

count = 0
for i in all_img_names:
    pic_path = os.path.join(path_train_ndmg, i)
    img = plt.imread(pic_path)
    x_train_ndmg.append(img)

y_train_ndmg = [0]*len(x_train_ndmg)

x_train = x_train_dmg + x_train_ndmg
y_train = y_train_dmg + y_train_ndmg

# x_train, y_train = shuffle(x_train, y_train)


#############################################

# test Data - Damaged
all_img_names = os.listdir(path_test_dmg)
x_test_dmg = list()

count = 0
for i in all_img_names:
    pic_path = os.path.join(path_test_dmg, i)
    img = plt.imread(pic_path)
    x_test_dmg.append(img)

y_test_dmg = [1]*len(x_test_dmg)

# test Data - Not Damaged
all_img_names = os.listdir(path_test_ndmg)
x_test_ndmg = list()

count = 0
for i in all_img_names:
    pic_path = os.path.join(path_test_ndmg, i)
    img = plt.imread(pic_path)
    x_test_ndmg.append(img)

y_test_ndmg = [0]*len(x_test_ndmg)

x_test = x_test_dmg + x_test_ndmg
y_test = y_test_dmg + y_test_ndmg

##### Model
x_train = np.array(x_train)
x_test = np.array(x_test)

from skimage.transform import resize
# plt.imshow(x_train[5])
# resized_image = resize(x_train[0], (128, 128, 3))
# img = plt.imshow(resized_image)

x_train = x_train / 255
x_test = x_test / 255

y_train = np.asarray(y_train).astype('float32').reshape((-1,1))
y_test = np.asarray(y_test).astype('float32').reshape((-1,1))

y_train_one_hot = to_categorical(y_train)
y_test_one_hot = to_categorical(y_test)

# MODEL
model = Sequential()
model.add(Conv2D(128, (5, 5), activation='relu', input_shape=(128, 128, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, (5, 5), activation='relu', input_shape=(128, 128, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dense(500, activation='relu'))
model.add(Flatten())
model.add(Dense(250, activation='relu'))
model.add(Dense(2, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

hist = model.fit(x_train, y_train_one_hot,
                 batch_size=256,
                 epochs=5,
                 validation_split=0.2)

result = model.evaluate(x_test, y_test_one_hot)[1]
print('the model is accurate to: ' + str(round(result, 4)*100) + "%")

plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()


import tensorflow as tf

file_path = r"/Users/jbheurtel/Downloads/task_9-18-2018 wallace, nc-2022_03_18_14_30_14-tfrecord 1.0/default.tfrecord"

dset_size = 0
reader = tf.TFRecordReader()
for example in tf.python_io.tf_record_iterator(file_path):
    dset_size = dset_size + 1

train_size = int(0.7 * dset_size)
val_size = int(0.15 * dset_size)
test_size = int(0.15 * dset_size)

full_dataset = tf.data.TFRecordDataset(file_path)
full_dataset = full_dataset.shuffle(dset_size)

# train
train_dataset = full_dataset.take(train_size)

# cutting the full_dataset and getting test_dataset
test_dataset = full_dataset.skip(train_size)
test_dataset = test_dataset.take(test_size)

# cutting the test_dataset and getting val_dataset
val_dataset = test_dataset.skip(test_size)
val_dataset = val_dataset.take(val_size)

with tf.io.TFRecordWriter(file_path)(r"/Users/jbheurtel/Desktop/MT2/tf_test/workspace/data/train.tfrecord", "w") as file:
    file.write(train_dataset)


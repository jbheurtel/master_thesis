import tensorflow as tf

record_path = r"/Users/jbheurtel/Desktop/MT2/tf_test/workspace/data/default.tfrecord"

filenames = [record_path]
raw_dataset = tf.data.TFRecordDataset(filenames)

# the take method here takes one screenshot data.
for raw_record in raw_dataset.take(30):
    example = tf.train.Example()
    example.ParseFromString(raw_record.numpy())
    print(example)



# as seen here in this example, the dict is structured as follows

# This is an image for which there is only one element:

# features:
# - image/encoded
# - image/filename
# - image/format
# - image/height
# - image/key/sha256
# - image/object/bbox/xmax -> one value
# - image/object/bbox/xmin -> one value
# - image/object/bbox/ymax -> one value
# - image/object/bbox/ymin -> one value
# - image/object/class/label -> one value
# - image/object/class/text -> one value
# - image/source_id
# - image/width

# This is an image for which there is only one element:

# features:
# - image/encoded
# - image/filename
# - image/format
# - image/height
# - image/key/sha256
# - image/object/bbox/xmax -> multiple values
# - image/object/bbox/xmin -> multiple values
# - image/object/bbox/ymax -> multiple values
# - image/object/bbox/ymin -> multiple values
# - image/object/class/label -> multiple values
# - image/object/class/text -> multiple values
# - image/source_id
# - image/width

def get_dataset_partitions_tf(ds, ds_size, train_split=0.8, val_split=0.1, test_split=0.1, shuffle=True,
                              shuffle_size=10000):
    assert (train_split + test_split + val_split) == 1

    if shuffle:
        # Specify seed to always have the same split distribution between runs
        ds = ds.shuffle(shuffle_size, seed=12)

    train_size = int(train_split * ds_size)
    val_size = int(val_split * ds_size)

    train_ds = ds.take(train_size)
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)

    return train_ds, val_ds, test_ds


import numpy as np

# Write the records to a file.
example_path = r"/Users/jbheurtel/Desktop/MT2/tf_test/workspace/data/tests.tfrecord"
with tf.io.TFRecordWriter(example_path) as file_writer:
  for _ in range(4):
    x, y = np.random.random(), np.random.random()

    record_bytes = tf.train.Example(features=tf.train.Features(feature={
        "x": tf.train.Feature(float_list=tf.train.FloatList(value=[x])),
        "y": tf.train.Feature(float_list=tf.train.FloatList(value=[y])),
    })).SerializeToString()
    file_writer.write(record_bytes)

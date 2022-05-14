import os
import pandas as pd
import shutil
import tensorflow as tf
import yaml

from main.data.code_xml_to_csv import xml_to_csv
from main.data.code_csv_to_tfrecords import create_tf_example

from main.data.__init__ import __version__


def transform_annotated_data():

    conf = get_config

    fldr_raws = r"/Users/jean-baptisteheurtel/Main/university/masters/Thesis/1. data/annotated"
    output_path = r"/Users/jean-baptisteheurtel/Main/university/masters/Thesis/1. data/annotated_transformed"

    label_map_path = os.path.join(self.paths.data.root, "label_map.yaml")

    for data_set in self.params.data_sets:
        load_images(os.path.join(self.conf.paths.cvat, data_set), self.paths.data.root)

    if self.params.group_flooded:
        refactor_annotations(annotations_path)

    build_label_map(annotations_path=annotations_path, dest_path=label_map_path)
    build_tf_records(data_root=self.paths.data.root, images_root=self.paths.data.images,
                     split_params=self.params.split_params, label_map=self.data["label_map"])




def refactor_annotations(annotations_path):
    try:
        print("refactoring annotations")
        group_dict = {"flooded_severe": "flooded",
                      "flooded_mild": "flooded",
                      "non_flooded": "non_flooded"}

        annotations = pd.read_csv(annotations_path)
        col_annot = annotations["class"]
        col_annot = col_annot.apply(lambda x: str([group_dict[i] for i in eval(x)]))
        annotations["class"] = col_annot
        annotations.to_csv(annotations_path)
    except KeyError:
        print("already refactored annotations")


def build_label_map(annotations_path, dest_path):
    annotations = pd.read_csv(annotations_path)

    # building label map
    label_map = dict()
    classes = annotations["class"].to_list()
    classes = [eval(x) for x in classes]
    classes = set([item for sublist in classes for item in sublist])
    count = 0
    for i in classes:
        label_map[i] = count
        count = count + 1

    with open(dest_path, "w") as file:
        yaml.dump(label_map, file)
    return label_map


def build_tf_records(data_root, images_root, split_params: dict, label_map):
    print("building tf_records")
    xml_csv = pd.read_csv(os.path.join(data_root, "annotations.csv"))

    n = len(xml_csv)
    n_train, n_val, n_test = (n * split_params["train"], n * split_params["validation"], n * split_params["test"])
    xml_csv = xml_csv.sample(frac=1)

    data_dict = dict()
    data_dict["train"] = xml_csv.take(range(round(n_train)), axis=0)
    data_dict["validation"] = xml_csv.loc[set(xml_csv.index) - set(data_dict["train"].index)].take(
        range(round(n_val)))
    data_dict["test"] = xml_csv.loc[
        set(xml_csv.index) - set(data_dict["train"].index) - set(data_dict["validation"].index)]

    # Serialize csv
    for df_name, df in data_dict.items():
        record_path = os.path.join(data_root, df_name + ".record")
        writer = tf.io.TFRecordWriter(record_path)
        for group in df.iterrows():
            img_path = os.path.join(images_root, group[1].filename)
            new_img_path = os.path.join(data_root, df_name, group[1].filename)
            shutil.copyfile(img_path, new_img_path)
            tf_example = create_tf_example(group[1], img_path, label_map)
            os.remove(img_path)
            writer.write(tf_example.SerializeToString())
        writer.close()


def load_images(input_dir, ws_data_path):
    xml_path = os.path.join(input_dir, "annotations.xml")
    xml_df = xml_to_csv(xml_path)
    imgs = set(xml_df.filename)

    csv_name = "annotations.csv"
    csv_path = os.path.join(ws_data_path, csv_name)
    xml_df.to_csv(csv_path, index=None)

    for img in imgs:
        scr = os.path.join(input_dir, img)
        dest = os.path.join(ws_data_path, "images", img)
        shutil.copyfile(scr, dest)

    print("adding: " + str(len(imgs)) + " new images to the dataset")

# def parametrize_model_configs(self):
#
#     print("éiné")
#     self.configs = {
#         'num_classes': len(self.data["label_map"].keys()),
#         'feature_extractor_type': self.params.model,
#         'batch_size': 6,
#         'fine_tune_checkpoint_path': os.path.join(self.paths.model, self.params.model, "model", "checkpoint"),
#         'fine_tune_checkpoint_type': "detection",
#
#         'train_record_path' : os.path.join(self.paths.data.root, "train.record"),
#         'train_label_map_path': os.path.join(self.paths.data.root, "label_map.yaml"),
#
#         'test_record_path': os.path.join(self.paths.data.root, "test.record"),
#         'test_label_map_path': os.path.join(self.paths.data.root, "label_map.yaml")
#     }
#
#     config_file = os.path.join(self.conf.paths.models, self.params.model, "config_params.config.txt")
#
#     with open(config_file, 'r') as f:
#         content = f.read()
#         f.close()
#
#     content.close
#     content.format(**self.configs)
#
#     )


# def _copy_model_config(model_name, models_fldr_proj, models_fldr_ws):
#     model_config_file = model_name + ".config"
#     proj_model_config_path = os.path.join(models_fldr_proj, model_config_file)
#     ws_model_config_path = os.path.join(models_fldr_ws, model_config_file)
#     shutil.copyfile(proj_model_config_path, ws_model_config_path)
#     return ws_model_config_path

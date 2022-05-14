import argparse
import configparser
import os
import pandas as pd
import shutil
import tensorflow as tf
import yaml

from main.data.code_xml_to_csv import xml_to_csv
from main.data.code_csv_to_tfrecords import create_tf_example

from main.data.util import get_config, Map


class ParamLoader:
    def __init__(self, id):
        # loading parameter set
        conf = get_config()
        params = pd.read_excel(conf.paths.param_file, sheet_name='main')
        data_keys = pd.read_excel(conf.paths.param_file, sheet_name='data_key')
        split_keys = pd.read_excel(conf.paths.param_file, sheet_name='split_key')

        params = params.set_index("id")
        param_line = params.loc[id]

        # basic elements
        self.id = id
        self.nickname = param_line.loc["nickname"]
        self.data_key = param_line.loc["data_key"]
        self.split_key = param_line.loc["split_key"]
        self.group_flooded = bool(param_line.loc["group_flooded"])
        self.model = param_line.loc["model"]

        # interpreting keys
        self.data_sets = data_keys.set_index("key").loc[self.data_key]["dataset"].values

        self.split_params = split_keys.set_index("key").loc[self.split_key].set_index("part")["value"].to_dict()
        self.split_params = {k: v / sum(self.split_params.values()) for k, v in self.split_params.items()}
        self.split_params = Map(self.split_params)


class WorkSpace:
    def __init__(self, params: ParamLoader):
        self.conf = get_config()
        self.params = params
        self.name = params.nickname
        self.ws_root = os.path.join(self.conf.paths.ws, self.name)
        self.paths = _setup_folders(self.ws_root)
        # self.paths["model_config"] = _copy_model_config(self.params.model, self.conf.paths.models, self.paths.model)

    def build_data_set(self):

        self.data = Map()
        annotations_path = os.path.join(self.paths.data.root, "annotations.csv")
        label_map_path = os.path.join(self.paths.data.root, "label_map.yaml")
        # 1. Loading data sets into the repo
        for data_set in self.params.data_sets:
            load_images(os.path.join(self.conf.paths.cvat, data_set), self.paths.data.root)

        if self.params.group_flooded:
            refactor_annotations(annotations_path)

        self.data["label_map"] = build_label_map(annotations_path, label_map_path)
        build_tf_records(data_root=self.paths.data.root,
                         images_root=self.paths.data.images,
                         split_params=self.params.split_params,
                         label_map=self.data["label_map"])

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


def load_images(input_dir, data_dir):
    xml_path = os.path.join(input_dir, "annotations.xml")
    xml_df = xml_to_csv(xml_path)
    new_imgs = set(xml_df.filename)

    csv_name = "annotations.csv"
    csv_path = os.path.join(data_dir, csv_name)
    if not os.path.exists(csv_path):
        xml_df.to_csv(csv_path, index=None)
    else:
        existing_csv = pd.read_csv(csv_path)
        ids = set(existing_csv.filename)
        new_imgs = new_imgs - ids
        xml_df = xml_df.loc[xml_df.filename.apply(lambda x: x in new_imgs)]
        xml_df = pd.concat([existing_csv, xml_df], axis=0)
        xml_df.to_csv(csv_path, index=None)

    for img in new_imgs:
        scr = os.path.join(input_dir, img)
        dest = os.path.join(data_dir, "images", img)
        shutil.copyfile(scr, dest)

    print("adding: " + str(len(new_imgs)) + " new images to the dataset")


def _setup_folders(ws_root):
    paths = Map()
    paths["ws"] = ws_root
    paths["data"] = Map()
    paths.data["root"] = os.path.join(ws_root, "data")
    paths.data["images"] = os.path.join(ws_root, "data/images")
    paths.data["train"] = os.path.join(ws_root, "data/train")
    paths.data["validation"] = os.path.join(ws_root, "data/validation")
    paths.data["test"] = os.path.join(ws_root, "data/test")
    paths["model"] = os.path.join(ws_root, "model")
    paths["results"] = os.path.join(ws_root, "results")

    dir_list = list(paths.values()) + list(paths.data.values())
    dir_list = [x for x in dir_list if type(x) == str]

    for dir_path in dir_list:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            print("creating directory: " + dir_path)
        else:
            print(dir_path, "- exists")

    return paths


if __name__ == '__main__':
    os.chdir(r"/Users/jbheurtel/Desktop/MT2")

    # parser = argparse.ArgumentParser()
    # parser.add_argument("-id", "--param_key", type=int)
    # args = parser.parse_args()

    args = Map()
    args["id"] = 1

    shutil.rmtree(r"/Users/jbheurtel/Desktop/MT2_WS/test_ws_1")

    param = ParamLoader(args.id)
    ws = WorkSpace(param)
    ws.build_data_set()
    ws.parametrize_model_configs()

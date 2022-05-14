import os
import argparse

import yaml

from config.config import get_paths
from toolbox.util import Map

from main.parameters.base import ParamLoader
from main.data.base import load_images, refactor_annotations, build_label_map, build_tf_records


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

    for dir in dir_list:
        os.mkdir(dir)
        print("creating directory: " + dir)

    return paths


def _build_logger(ws_root):
    name = "workflow_logger"
    logger_path = os.path.join(ws_root, name + ".yaml")
    if not os.path.exists(logger_path):
        logger = dict()
        with open(logger_path, "w") as f:
            yaml.dump(logger , f)
    return logger_path



class WorkSpace(dict):
    def __init__(self, params: ParamLoader):

        # create a config file.

        self["proj_paths"] = get_paths()
        self["name"] = params.nickname
        self["params"] = params
        self["ws_root"] = os.path.join(self["proj_paths"].ws, self["name"])

        # 0. getting paths
        annotations_path = os.path.join(self.paths.data.root, "annotations.csv")
        label_map_path = os.path.join(self.paths.data.root, "label_map.yaml")

        for data_set in self.params.data_sets:
            load_images(os.path.join(self.conf.paths.cvat, data_set), self.paths.data.root)

        if self.params.group_flooded:
            refactor_annotations(annotations_path)

        build_label_map(annotations_path=annotations_path, dest_path=label_map_path)
        build_tf_records(data_root=self.paths.data.root, images_root=self.paths.data.images,
                         split_params=self.params.split_params, label_map=self.data["label_map"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int)
    args = parser.parse_args()
    param = ParamLoader(args.id)

    # initialize workspace
    ws = WorkSpace(param)
    # ws.build_data_set()

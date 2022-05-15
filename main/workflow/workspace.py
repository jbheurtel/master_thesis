import os
import yaml

from toolbox.config import get_config
from toolbox.util import NestedDictValues

from main.parameters.base import ParamLoader


class WorkSpace:
    def __init__(self, params: ParamLoader):

        # create a config file.
        self.gen_conf = get_config()
        self.params = params.to_dict()
        self.name = self.params["nickname"]
        self.root = os.path.join(self.gen_conf["ws"], self.name)
        self.conf_path = os.path.join(self.root, "conf.yaml")

    def initialize(self):
        self._define_paths()
        self._build_root()
        self._build_fldr_structure()
        self._save_configs()

    def get_config(self):
        with open(self.conf_path) as file:
            conf = yaml.load(file, Loader=yaml.Loader)
        return conf

    def _define_paths(self):
        conf = get_config()
        self.paths = dict()
        self.paths["ws_root"] = os.path.join(conf.ws, self.name)
        self.paths["data"] = dict()
        self.paths["data"]["root"] = os.path.join(self.paths["ws_root"], "data")
        for i in ("train", "validation", "test"):
            self.paths["data"][i] = dict()
            self.paths["data"][i]["root"] = os.path.join(self.paths["ws_root"], "data", i)
            self.paths["data"][i]["images"] = os.path.join(self.paths["data"][i]["root"], "images")
        self.paths["model"] = os.path.join(self.paths["ws_root"], "model")
        self.paths["results"] = os.path.join(self.paths["ws_root"], "results")

    def _build_root(self):
        if not os.path.exists(self.paths["ws_root"]):
            os.mkdir(self.paths["ws_root"])

    def _build_fldr_structure(self):
        dir_list = list(NestedDictValues(self.paths))
        for dir in dir_list:
            if not os.path.exists(dir):
                os.mkdir(dir)
                print("creating directory: " + dir)

    def _save_configs(self):
        conf = dict()
        conf["params"] = self.params
        conf["paths"] = self.paths
        conf["root"] = self.root

        with open(self.conf_path , "w") as file:
            yaml.dump(conf, file)


if __name__ == '__main__':
    params = ParamLoader("2")
    ws = WorkSpace(params)
    ws.initialize()
    conf = ws.get_config()







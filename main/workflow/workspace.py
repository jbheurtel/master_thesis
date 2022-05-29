import os
import shutil

import yaml

from toolbox.config import get_config
from toolbox.util import Map, NestedDictValues

from main.parameters.base import ParamLoader


class WorkSpace:
    def __init__(self, params: ParamLoader, reset=False):

        # create a config file.
        self.conf = get_config()
        self.params = params.to_Map()
        self.name = self.params["nickname"]
        self.root = os.path.join(self.conf["workspace"], self.name)
        # self.conf_path = os.path.join(self.root, "conf.yaml")
        self.p = Map()
        self.p["root"] = self.root

        if reset:
            self._reset()

        self._build_root()
        self._build_folder_structure()

    def _mkdir(self, dir_name):
        path = os.path.join(self.root, dir_name)
        if not os.path.exists(path):
            os.mkdir(os.path.join(self.root, dir_name))
            self.p[dir_name] = path

    def _reset(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    def _build_folder_structure(self):
        self.p["data"] = os.path.join(self.p["root"], "data")
        self.p["data_imports"] = os.path.join(self.p["data"], "import")
        self.p["data_transformed"] = os.path.join(self.p["data"], "transformed")
        self.p["model"] = os.path.join(self.p["root"], "model")
        self.p["results"] = os.path.join(self.p["root"], "results")

        for path in self.p.values():
            if not os.path.exists(path):
                os.mkdir(path)
                print("building: " + os.path.basename(path))
            else:
                print("not building: " + os.path.basename(path) + " - already there")

    def get_config(self):
        with open(self.conf_path) as file:
            conf = yaml.load(file, Loader=yaml.Loader)
        return conf

    def import_data(self):

        for img_set in self.params["data_sets"]:
            source = os.path.join(self.conf.data_annotated, img_set)
            destination = os.path.join(self.p["data_imports"], img_set)
            print("copying: " + img_set)
            shutil.copytree(source, destination)
            print("finished copying: " + img_set)

    def _build_root(self):
        if not os.path.exists(self.p["root"]):
            os.mkdir(self.p["root"])

    def _init_configs(self):
        conf = dict()
        conf["params"] = self.params
        conf["paths"] = self.paths
        conf["root"] = self.root
        self.conf = conf

    def save_configs(self, conf):
        with open(self.conf_path , "w") as file:
            yaml.dump(conf, file)


if __name__ == '__main__':
    params = ParamLoader("2")
    ws = WorkSpace(params)
    ws.initialize()
    conf = ws.get_config()







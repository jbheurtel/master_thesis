import os
import yaml

from toolbox.util import Map
from toolbox.config import get_config

from main.parameters.base import ParamLoader


class WorkSpace():
    def __init__(self, params: ParamLoader):

        # create a config file.
        self.name = params.nickname
        self.params = params

        self._define_paths()
        self._build_root()
        self._build_fldr_structure()
        self._save_params()

    def _define_paths(self):
        conf = get_config()
        self.paths = Map()
        self.paths["ws_root"] = os.path.join(conf.ws, self.name)
        self.paths["data"] = Map()
        self.paths.data["root"] = os.path.join(self.paths["ws_root"], "data")
        self.paths.data["images"] = os.path.join(self.paths["ws_root"], "data/images")
        self.paths.data["train"] = os.path.join(self.paths["ws_root"], "data/train")
        self.paths.data["validation"] = os.path.join(self.paths["ws_root"], "data/validation")
        self.paths.data["test"] = os.path.join(self.paths["ws_root"], "data/test")
        self.paths["model"] = os.path.join(self.paths["ws_root"], "model")
        self.paths["results"] = os.path.join(self.paths["ws_root"], "results")

    def _build_root(self):
        if not os.path.exists(self.paths.ws_root):
            os.mkdir(self.paths.ws_root)

    def _build_fldr_structure(self):
        dir_list = list(self.paths.values()) + list(self.paths.data.values())
        dir_list = [x for x in dir_list if type(x) == str]
        for dir in dir_list:
            if not os.path.exists(dir):
                os.mkdir(dir)
                print("creating directory: " + dir)

    def _save_params(self):
        params_path = os.path.join(self.paths.ws_root, "params.yaml")
        params = dict(self.params)
        params["split_params"] = dict(params["split_params"])
        with open(params_path, "w") as file:
            yaml.dump(params, file)


def get_params(ws_root):
    param_path = os.path.join(ws_root, "params.yaml")
    with open(param_path) as file:
        params = yaml.load(file, Loader=yaml.Loader)
    return params


if __name__ == '__main__':
    params = ParamLoader("2")
    WorkSpace(params)






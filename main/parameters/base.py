import os
import yaml

import pandas as pd

from toolbox.config import get_config
from toolbox.util import Map

from main.parameters import __version__


class ParamLoader:
    def __init__(self, id):
        # loading parameter set
        conf = get_config()
        param_file = os.path.join(conf.param, "param_" + __version__ + ".xls")
        params = pd.read_excel(param_file, sheet_name='main')
        data_keys = pd.read_excel(param_file, sheet_name='data_key', index_col=0)
        split_keys = pd.read_excel(param_file, sheet_name='split_key', index_col=0)
        label_keys = pd.read_excel(param_file, sheet_name='label_key', index_col=0)

        params = params.set_index("id")
        param_line = params.loc[int(id)]

        # basic elements
        self.id = id
        self.nickname = param_line.loc["nickname"]
        self.data_key = param_line.loc["data_key"]
        self.split_key = param_line.loc["split_key"]
        self.label_key = None if param_line.loc["label_key"] == 0 else param_line.loc["label_key"]
        self.model = param_line.loc["model"]

        # interpreting keys
        dsets = data_keys.loc[self.data_key]["dataset"]
        if isinstance(dsets, str):
            self.data_sets = [dsets]
        else:
            self.data_sets = list(dsets)

        self.split_params = split_keys.loc[self.split_key].set_index("part")["value"].to_dict()
        self.split_params = {k: v / sum(self.split_params.values()) for k, v in self.split_params.items()}

        if self.label_key is not None:
            self.label_map_dict = label_keys.loc[self.label_key].set_index("original_name")["group"].to_dict()
        else:
            self.label_map_dict = dict()

    def to_Map(self):
        params = Map()
        params["id"] = self.id
        params["nickname"] = self.nickname
        params["data_key"] = self.data_key
        params["split_key"] = self.split_key
        params["label_key"] = self.label_key
        params["model"] = self.model
        params["split_params"] = self.split_params
        params["data_sets"] = self.data_sets
        params["label_map_dict"] = self.label_map_dict
        return params

    def get_root(self):
        conf = get_config()
        return os.path.join(conf["ws"], self.nickname)


def get_params(ws_root):
    param_path = os.path.join(ws_root, "params.yaml")
    with open(param_path) as file:
        params = yaml.load(file, Loader=yaml.Loader)
    return params


if __name__ == "__main__":
    ParamLoader("1")

# params need to be saved somewhere
import os
import yaml

import pandas as pd

from toolbox.util import Map
from toolbox.config import get_config

from main.parameters import __version__


class ParamLoader(Map):
    def __init__(self, id):
        # loading parameter set
        conf = get_config()
        param_file = conf.param + "_" + __version__ + ".xls"
        params = pd.read_excel(param_file, sheet_name='main')
        data_keys = pd.read_excel(param_file, sheet_name='data_key')
        split_keys = pd.read_excel(param_file, sheet_name='split_key')

        params = params.set_index("id")
        param_line = params.loc[int(id)]

        # basic elements
        self.id = id
        self.nickname = param_line.loc["nickname"]
        self.data_key = param_line.loc["data_key"]
        self.split_key = param_line.loc["split_key"]
        self.group_flooded = bool(param_line.loc["group_flooded"])
        self.model = param_line.loc["model"]

        # interpreting keys
        dsets = data_keys.set_index("key").loc[self.data_key]["dataset"]
        if isinstance(dsets, str):
            self.data_sets = [dsets]
        else:
            self.data_sets = list(dsets)

        self.split_params = split_keys.set_index("key").loc[self.split_key].set_index("part")["value"].to_dict()
        self.split_params = {k: v / sum(self.split_params.values()) for k, v in self.split_params.items()}
        self.split_params = Map(self.split_params)


def get_params(ws_root):
    param_path = os.path.join(ws_root, "params.yaml")
    with open(param_path) as file:
        params = yaml.load(file, Loader=yaml.Loader)
    return params


if __name__ == "__main__":
    ParamLoader("1")
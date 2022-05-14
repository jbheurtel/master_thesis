import os
import argparse

import pandas as pd
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

        # interpreting keys
        self.data_sets = data_keys.set_index("key").loc[self.data_key]["dataset"].values

        self.split_params = split_keys.set_index("key").loc[self.split_key].set_index("part")["value"].to_dict()
        self.split_params = {k: v/sum(self.split_params.values()) for k, v in self.split_params.items()}
        self.split_params = Map(self.split_params)


if __name__ == '__main__':
    os.chdir(r"/Users/jbheurtel/Desktop/MT2")

    # parser = argparse.ArgumentParser()
    # parser.add_argument("-id", "--param_key", type=int)
    # args = parser.parse_args()

    args = Map()
    args["id"] = 1

    param = ParamLoader(args.id)
    ws = WorkSpace(param)
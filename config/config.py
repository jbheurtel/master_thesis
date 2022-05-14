from toolbox.util import Map, find
import os
import yaml
import importlib_resources
from pathlib import Path


def get_paths():

    paths = Map()

    # root
    root = Path(__file__).parent.parent
    paths["root"] = root

    for i in os.listdir(root):
        if "." not in i:
            paths[i] = os.path.join(root, i)

    paths["param_set"] = find("param.xls", root)
    paths["cvat"] = os.path.join(paths.dataset, "cvat")

    with importlib_resources.path("config", "config.yaml") as p:
        path = str(p)
    with open(path) as file:
        configs = yaml.full_load(file)

    paths["ws"] = configs["ws"]

    return paths

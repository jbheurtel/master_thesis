import os
import yaml


def fmt_proj(s: str):
    ix = s.rfind(".")
    if ix != -1:
        extension = s[ix:]
    else:
        extension = ""

    ns = s.replace(extension, "")
    ns = ns.replace(" ", "_")
    ns = ns.replace("-", "")
    ns = ns.lower()
    ns = ns.replace(".", "")

    ns = ns.replace("(", "")
    ns = ns.replace(")", "")

    if extension == ".png":
        ns = ns.replace("_at_", "_")
        ns = ns.replace("screen_shot_", "")

    return ns + extension


class Map(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get_config():
    with open(os.path.join(os.getcwd(), "config/config.yaml")) as file:
        configs = yaml.full_load(file)
        map_configs = Map(configs)
        map_configs.paths = Map(map_configs.paths)
        return map_configs
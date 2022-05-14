import os
import yaml
import getpass
from toolbox.util import Map


def get_config():
    usr = getpass.getuser()
    thesis_fldr = os.path.join('/Users', usr, 'Documents/thesis')
    config_file = os.path.join(thesis_fldr, "config.yaml")
    with open(config_file) as file:
        conf = yaml.full_load(file)

    data = Map(conf["data"])
    conf = Map(conf)
    conf.data = data
    return conf

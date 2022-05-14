import os

import pandas as pd

from toolbox.config import get_config

from main.parameters.base import get_params
from main.data import __version__

# loads from prepped data, based on parameters.

def load_data(workspace_root):
    params = get_params(workspace_root)
    conf = get_config()

    # copy csvs.
    annotations = pd.DataFrame()
    for img_group in params["data_sets"]:
        path_annotations = os.path.join(conf.data.annotated_transformed, __version__, img_group, "annotations.csv")
        grp_annotations = pd.read_csv(path_annotations)
        grp_annotations["img_group"] = img_group
        annotations = pd.concat([annotations, grp_annotations])

    annotations.to_csv()

if __name__ == "__main__":
    workspace_root = r"/Users/jean-baptisteheurtel/Main/university/masters/Thesis/02_workspace/test_ws_2"
    load_data(workspace_root)
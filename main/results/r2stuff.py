import os

import pandas as pd

from toolbox.config import get_config

model = "mgrain"
res_folder = get_config().results
analyses_path_train = os.path.join(res_folder, model, "train", "analyses")
analyses_path_val = os.path.join(res_folder, model, "val", "analyses")

csv_train = pd.read_csv(os.path.join(analyses_path_train, "res_dmg_area.csv"), index_col=0)
csv_val = pd.read_csv(os.path.join(analyses_path_val, "res_dmg_area.csv"), index_col=0)

a = pd.concat([csv_train, csv_val], join="inner", axis=1)["R2"]
a.columns = ["train", "val"]
a = a.loc[(a.train > 0) * (a.val > 0)]
a.plot(xlabel="detection threshold", ylabel="R2")


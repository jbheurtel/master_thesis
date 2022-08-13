import os

import pandas as pd
import matplotlib.pyplot as plt

from toolbox.config import get_config


res_folder = get_config().results
os.listdir(res_folder)

res = dict()
model_types = ["lgrain", "hgrain", "mgrain"]

for i in model_types:
    csv_path = os.path.join(res_folder, i, "train_log.csv")
    res[i] = pd.read_csv(csv_path)

loss_types = {i for i in res["lgrain"].columns if "loss" in i} - {"det_loss", "reg_l2_loss"}

main_df = pd.DataFrame()
for i in res.values():
    main_df = pd.concat([main_df, i], axis=1)

loss_dfs = dict()
for i in loss_types:
    df = main_df[i]
    df.columns = model_types
    loss_dfs[i] = df

len(loss_dfs)


figure, axis = plt.subplots(1, 3, figsize = (12, 4))
series = [0, 1, 2]
positions = {list(loss_dfs)[i] : series[i] for i in range(len(loss_types))}

for loss_type, pos in positions.items():
    axis[pos].plot(loss_dfs[loss_type], label = model_types)
    axis[pos].legend()
    axis[pos].set_title(loss_type)

plt.show()
plt.savefig(os.path.join(res_folder, "loss_summary.eps"))




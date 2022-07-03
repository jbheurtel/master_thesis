import os
import collections

import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

from toolbox.config import get_config

from main.model.detection import _COLOR_PALETTE

tuple(i/256 for i in _COLOR_PALETTE["house"])


def plot_scores(scores, name=None):
    for dmg_type, score_dict in scores.items():

        data = {k: v for k, v in score_dict.items() if v != (0, 0)}
        x = [i[1] for i in data.values()]
        y = [i[0] for i in data.values()]
        annotations = [str(k) for k in data.keys()]

        if len(data) > 0:
            if len(data) > 1:
                plt.plot(x, y, c=tuple(i/256 for i in _COLOR_PALETTE[dmg_type]), label=dmg_type)
            else:
                plt.scatter(x, y, c=tuple(i / 256 for i in _COLOR_PALETTE[dmg_type]), label=dmg_type)

            for i, label in enumerate(annotations):
                plt.annotate(label, (x[i], y[i]))

    if name:
        title_extension = " - " + name + " data"
    else:
        title_extension = ""

    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel("recall")
    plt.ylabel("accuracy")
    plt.title("accuracy-recall tradoff" + title_extension)
    plt.grid()
    plt.legend(loc="upper left")
    return plt


def analyse_dmg_area_results(model_name, sub):
    conf = get_config()
    res_fldr = conf.results

    assert sub in ["train", "val"]

    data_folder = os.path.join(res_fldr, model_name, sub)
    data_folder = [os.path.join(data_folder, i) for i in os.listdir(data_folder)]
    df_list = [i for i in data_folder if ".csv" in i]
    df_dict = {int(os.path.basename(i)[os.path.basename(i).rfind(".csv") - 2:os.path.basename(i).rfind(".csv")]) / 10: i
               for i in df_list}
    df_dict = collections.OrderedDict(sorted(df_dict.items()))

    res_df = pd.DataFrame(columns=["MSE", "MAE", "RMSE", "R2"], index=df_dict.keys())

    for dt, csv_path in df_dict.items():
        df = pd.read_csv(csv_path, index_col=0).set_index("img_name")
        y = np.array(df["obs_dmg"])
        y_hat = np.array(df["pred_dmg"])

        d = y - y_hat
        res_df.loc[dt, "MSE"] = round(np.mean(d ** 2), 4)
        res_df.loc[dt, "MAE"] = round(np.mean(abs(d)), 4)
        res_df.loc[dt, "RMSE"] = round(np.sqrt(res_df.loc[dt, "MSE"]), 4)
        res_df.loc[dt, "R2"] = round(1 - (sum(d ** 2) / sum((y - np.mean(y)) ** 2)), 4)

    return res_df

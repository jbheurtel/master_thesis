import os
import collections
from matplotlib import pyplot as plt
import random

import pandas as pd
import numpy as np

from main.results.functions import get_threshold_value

from toolbox.config import get_config


costs = {
    "roof_damage": 25000,
    "roof_destruction": 50000,
    "wall_damage": 50000,
    "wall_destrution": 100000,
    "damage": 200000
}


def calc_damage(data, costs):

    data["damage_cost"] = data.apply(lambda x: x["damage"] * costs["damage"] +
                                               x["roof_damage"] * costs["roof_damage"] +
                                               x["wall_damage"] * costs["wall_damage"], axis=1)

    # data["damage_cost"] = data.apply(lambda x: x["damage_prop"] * costs["damage"], axis=1)

    return data.sum()["damage_cost"]


def analyse_sampling_fx(model_name, sub, dt):
    conf = get_config()
    res_fldr = conf.results

    data_folder = os.path.join(res_fldr, model_name, "final", sub)
    data_folder = [os.path.join(data_folder, i) for i in os.listdir(data_folder)]
    df_list = [i for i in data_folder if ".csv" in i]
    df_dict = {get_threshold_value(i): i for i in df_list}
    df_dict = collections.OrderedDict(sorted(df_dict.items()))

    csv_path = df_dict[dt]

    df = pd.read_csv(csv_path, index_col=0).set_index("img_name")
    df["dmg_type"] = df["dmg_type"].apply(lambda x: x.replace("damage_prop", "damage"))
    df["obj"] = df.obj.apply(lambda x: x[x.find("0"):])
    
    df_obs = df.pivot(index="obj", columns="dmg_type", values="obs_dmg")
    df_obs["damaged"] = df_obs.apply(lambda x: x.sum() != 0, axis=1)
    damaged_houses = set(df_obs["damaged"].loc[df_obs["damaged"]].index)

    df_obs = df_obs.loc[damaged_houses]


    df_pred = df.pivot(index="obj", columns="dmg_type", values="pred_dmg")
    df_pred = df_pred.loc[damaged_houses]

    costs = {
        "roof_damage": 25000,
        "roof_destruction": 50000,
        "wall_damage": 50000,
        "wall_destrution": 100000,
        "damage": 200000
    }

    costs = pd.Series(costs)
    costs = costs[[i  for i in costs.index if i in df_obs.columns]]
    df_pred = df_pred*costs
    df_pred["pred_costs"] = df_pred.sum(axis=1)

    df_obs = df_obs*costs
    df_obs["obs_costs"] = df_obs.sum(axis=1)

    combined = df_obs.join(df_pred["pred_costs"])[["pred_costs", "obs_costs"]]
    combined["r_diff"] = (combined["pred_costs"] - combined["obs_costs"])/combined["obs_costs"]
    mean, std = combined["r_diff"].mean(), combined["r_diff"].std()

    combined["r_diff"].hist(bins=200)

    sample_sizes = np.arange(1, 200, 1)
    to_plot = pd.DataFrame(index=sample_sizes, columns=["mean", "upper", "lower"])
    to_plot["mean"] = mean
    to_plot["upper"] = to_plot.apply(lambda x : mean + 1.96 * std / np.sqrt(x.name), axis=1)
    to_plot["lower"] = to_plot.apply(lambda x: mean - 1.96 * std / np.sqrt(x.name), axis=1)

    fig = plt.figure()
    ax = to_plot["mean"].plot(grid=True, color="red", linestyle='dashed')
    ax = to_plot["upper"].plot(grid=True, color="blue")
    ax = to_plot["lower"].plot(grid=True, color="blue")
    plt.axhline(y=0, color='black', linestyle='-')
    ax.set_xlabel("sample size")
    ax.set_ylabel("average error")
    ax.set_title("detection threshold: " + str(dt))
    ax.set_ylim([-1.5, 1.5])
    ax.legend()
    fig.savefig('/Users/jean-baptisteheurtel/Main/2022/02_university/02_thesis/Thesis/10_results/TEST_' + str(dt) + '.svg')

    return fig


if __name__ == '__main__':
    model_name = "mgrain"
    sub = "train"
    dt = 0.1
    fig = analyse_sampling_fx(model_name, sub, dt)

import os

import pandas as pd

from main.results.functions import get_scores, get_f1_scores
from main.results.analyses import plot_scores, analyse_dmg_area_results, plot_f1_scores

from toolbox.config import get_config

def get_mean_f1(f1_scores, model):

    # OVERALL
    if model == "mgrain":
        F1 = pd.DataFrame(f1_scores)
        f1_all = F1.drop("damage", axis=1).mean(axis=1)
        f1_structures = F1.drop(["roof_damage", "damage", "wall_damage"], axis=1).mean(axis=1)
        f1_damages = F1.drop(["house", "destroyed_house", "damage"], axis=1).mean(axis=1)

    elif model == "hgrain":
        F1 = pd.DataFrame(f1_scores)
        f1_all = F1.drop("total_destruction", axis=1).mean(axis=1)
        f1_structures = F1.drop(["roof_damage", "total_destruction", "wall_damage", "wall_destruction", "roof_destruction"], axis=1).mean(axis=1)
        f1_damages = F1.drop(["house", "destroyed_house", "total_destruction"], axis=1).mean(axis=1)
    else:
        F1 = pd.DataFrame(f1_scores)
        f1_all = F1.mean(axis=1)
        f1_structures = pd.DataFrame(F1.drop(["damage"], axis=1).mean(axis=1))
        f1_damages = F1.drop(["house", "destroyed_house"], axis=1).mean(axis=1)

    all = pd.concat([f1_all, f1_structures, f1_damages], axis=1)
    all.columns = ["overall", "structures", "damages"]
    all = all.round(2)
    return all


if __name__ == "__main__":

    # INPUTS
    model = "hgrain"
    d_type = "val"

    res_folder = get_config().results
    analyses_path = os.path.join(res_folder, model, "final", d_type, "analyses")
    if not os.path.exists(analyses_path):
        os.mkdir(analyses_path)

    # PREPARATIONS
    scores = get_scores(model, d_type)

    import numpy as np

    if model=="hgrain":
        data = pd.DataFrame(scores).loc[0.3].drop("total_destruction")
    elif model=="mgrain":
        data = pd.DataFrame(scores).loc[0.3].drop("damage")
    elif model=="lgrain":
        data = pd.DataFrame(scores).loc[0.4]
    mAP = np.array([i[0] for i in data]).mean()
    mAS = np.array([i[1] for i in data]).mean()
    print("mAP: " + str(round(mAP, 3)))
    print("mAS: " + str(round(mAS, 3)))

    f1_scores = get_f1_scores(scores)
    mean_F1_scores = get_mean_f1(f1_scores, model)
    csv_path = os.path.join(analyses_path, "mean_f1.csv")
    mean_F1_scores.to_csv(csv_path)

    # AGGREGATORS
    plt = plot_scores(scores)
    scores_img_path = os.path.join(analyses_path, "confusion_scores.svg")
    plt.savefig(scores_img_path)

    plt_f1 = plot_f1_scores(f1_scores)
    f1_scores_img_path = os.path.join(analyses_path, "f1_scores.svg")
    plt_f1.savefig(f1_scores_img_path)

    df = analyse_dmg_area_results(model, d_type)
    csv_path = os.path.join(analyses_path, "res_dmg_area.csv")
    df.to_csv(csv_path)


from toolbox.config import get_config
import os
import collections

import re

import yaml
from main.model.util import labels_dict


def aggregate_cx(cx_dict, damage_types):
    cmx = {"TP": 0, "FP": 0, "FN": 0}
    final_cfmx = {i: cmx for i in damage_types}

    for cfmx in cx_dict.values():
        for k, v in final_cfmx.items():
            v2 = v.copy()
            v2["FN"] = v2["FN"] + cfmx[k]["FN"]
            v2["FP"] = v2["FP"] + cfmx[k]["FP"]
            v2["TP"] = v2["TP"] + cfmx[k]["TP"]
            final_cfmx[k] = v2

    return final_cfmx


def get_precision(cfmx):
    try:
        return cfmx["TP"] / (cfmx["FP"] + cfmx["TP"])
    except ZeroDivisionError:
        return 0


def get_recall(cfmx):
    try:
        return cfmx["TP"] / (cfmx["TP"] + cfmx["FN"])
    except ZeroDivisionError:
        return 0


def get_threshold_value(file_path):
    a = os.path.basename(file_path)
    numbers = re.findall(r'\d+', a)[0]
    return float("." + numbers[1:])


def get_scores(model_name, sub):
    labels = labels_dict[model_name]
    conf = get_config()
    res_fldr = conf.results

    assert sub in ["train", "val"]

    data_folder = os.path.join(res_fldr, model_name, "final", sub)
    data_folder = [os.path.join(data_folder, i) for i in os.listdir(data_folder)]
    cf_list = [i for i in data_folder if ((".yml" in i) or (".yaml" in i))]
    all_cfs = dict()

    for i in cf_list:
        dt = get_threshold_value(i)

        with open(i) as f:
            cm = yaml.full_load(f)
        all_cfs[dt] = cm

    agg_cfs = dict()
    scores = {i: {} for i in labels}
    for k, v in all_cfs.items():
        agg_cf = aggregate_cx(v, labels)
        agg_cfs[k] = agg_cf
        for dmg_type, cfmx in agg_cf.items():
            scores[dmg_type][k] = round(get_precision(cfmx), 3), round(get_recall(cfmx), 3)

    scores_2 = dict()
    for k, v in scores.items():
        od = collections.OrderedDict(sorted(v.items()))
        scores_2[k] = od

    return scores_2


def f1_score(precision, recall):
    if precision == 0 or recall == 0:
        return 0
    else:
        return (2 * precision * recall) / (precision + recall)


def get_f1_scores(scores):
    f1_scores = dict()
    for dmg_type, scores_dt in scores.items():
        f1_scores[dmg_type] = dict()
        for dt, (p, r) in scores_dt.items():
            f1_scores[dmg_type][dt] = round(f1_score(p, r), 3)

    return f1_scores

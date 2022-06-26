import os
from toolbox.util import Map


def get_config():

    key_main= "Thesis"
    paths = dict()

    cwd = os.getcwd()
    paths["main"] = cwd[:(cwd.rfind(key_main) + len(key_main))]

    key_proj = "project"
    paths["project"] = cwd[:(cwd.rfind(key_proj) + len(key_proj))]

    subs = {i for i in os.listdir(paths["main"]) if i[2] == "_"}
    fldrs_main = {"".join([ch for ch in i if ch.isalpha()]).lower() : i for i in subs}

    paths["data"] = os.path.join(paths["main"], fldrs_main["data"], "MAIN")

    fldrs_data = {"".join([ch for ch in i if ch.isalpha()]).lower() : i for i in os.listdir(paths["data"])}

    paths["data_annotated"] = os.path.join(paths["data"], fldrs_data["annotated"])
    paths["data_non_annotated"] = os.path.join(paths["data"], fldrs_data["nonannotated"])
    paths["data_annotated_transformed"] = os.path.join(paths["data"], fldrs_data["annotatedtransformed"])

    paths["workspace"] = os.path.join(paths["main"], fldrs_main["workspace"])
    paths["model"] = os.path.join(paths["main"], fldrs_main["pretrainedmodels"])
    paths["param"] = os.path.join(paths["main"], fldrs_main["param"])

    conf = Map(paths)
    return conf


if __name__ == "__main__":
    get_config()

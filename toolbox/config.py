import os
from toolbox.util import Map


def get_config():

    key_word = "Thesis"
    paths = dict()

    cwd = os.getcwd()
    paths["main"] = cwd[:(cwd.rfind(key_word) + len(key_word))]

    subs = {i for i in os.listdir(paths["main"]) if i[2] == "_"}
    fldrs_main = {"".join([ch for ch in i if ch.isalpha()]).lower() : i for i in subs}

    paths["data"] = os.path.join(paths["main"], fldrs_main["data"])

    data_subs = {i for i in os.listdir(paths["data"]) if i[2] == "_"}
    fldrs_data = {"".join([ch for ch in i if ch.isalpha()]).lower() : i for i in data_subs}

    paths["data_annotated"] = os.path.join(paths["data"], fldrs_data["annotated"])
    paths["data_non_annotated"] = os.path.join(paths["data"], fldrs_data["nonannotated"])
    paths["data_transformed"] = os.path.join(paths["data"], fldrs_data["annotatedtransformed"])

    paths["workspace"] = os.path.join(paths["main"], fldrs_main["workspace"])
    paths["model"] = os.path.join(paths["main"], fldrs_main["pretrainedmodels"])
    paths["param"] = os.path.join(paths["main"], fldrs_main["param"])

    conf = Map(paths)
    return conf


if __name__ == "__main__":
    get_config()

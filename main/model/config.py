import os
import shutil

from toolbox.config import get_config
from main.parameters.base import ParamLoader
from main.workflow.workspace import WorkSpace


def parametrize_model_configs(ws):
    conf = ws.get_config()
    main_paths = get_config()
    model = conf["params"]["model"]
    ws_model_fldr = conf["paths"]["model"]
    pt_models_fldr = main_paths["models"]

    config_path = copy_model_config(model, pt_models_fldr, ws_model_fldr)
    model_configs_dict = get_model_configs(conf)
    filled_config_path = fill_model_configs(config_path, model_configs_dict)


def fill_model_configs(input, model_configs: dict):
    with open(input) as file:
        model_config = file.readlines()

    model_config = "".join(model_config)
    for k, v in model_configs.items():
        model_config = model_config.replace(k, v)

    new_path = input.replace("TOFILL", "FILLED")
    lines = model_config.split("\n")
    with open(new_path, "w") as f:
        for line in lines:
            f.write(line)
            f.write('\n')

    new_path_config_extension = new_path.replace(".txt", ".config")
    shutil.copyfile(new_path, new_path_config_extension)

    return new_path


def copy_model_config(model_name, models_fldr_proj, models_fldr_ws):
    model_config_file = "TOFILL_pipeline.txt"
    proj_model_config_path = os.path.join(models_fldr_proj, model_name, model_config_file)
    ws_model_config_path = os.path.join(models_fldr_ws, model_config_file)
    shutil.copyfile(proj_model_config_path, ws_model_config_path)
    return ws_model_config_path


def get_model_configs(conf):
    label_map = conf["data"]["label_map"]
    model = conf["params"]["model"]
    ws_model_fldr = conf["paths"]["model"]
    ws_data_fldr = conf["paths"]["data"]["root"]

    model_configs = {

        'INPUT_num_classes': str(len(label_map.keys())),

        'INPUT_batch_size': str(6),

        'INPUT_fine_tune_checkpoint': '"' + os.path.join(ws_model_fldr, model, "model", "checkpoint") + '"',
        'INPUT_fine_tune_checkpoint_type': '"detection"',
        'INPUT_use_bfloat16': str(False),

        'INPUT_train_tf_record': '"' + os.path.join(ws_data_fldr, "train.record") + '"',
        'INPUT_train_label_map_path': '"' + os.path.join(ws_data_fldr, "label_map.pbtxt") + '"',

        'INPUT_test_tf_record': '"' + os.path.join(ws_data_fldr, "test.record") + '"',
        'INPUT_test_label_map_path': '"' + os.path.join(ws_data_fldr, "label_map.pbtxt") + '"'
    }

    return model_configs


def _copy_model_config(model_name, models_fldr_proj, models_fldr_ws):
    model_config_file = model_name + ".config"
    proj_model_config_path = os.path.join(models_fldr_proj, model_config_file)
    ws_model_config_path = os.path.join(models_fldr_ws, model_config_file)
    shutil.copyfile(proj_model_config_path, ws_model_config_path)
    return ws_model_config_path


if __name__ == "__main__":
    params = ParamLoader("1")
    ws = WorkSpace(params)
    parametrize_model_configs(ws)


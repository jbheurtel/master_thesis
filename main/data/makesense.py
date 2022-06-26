# get annotations from makespace

import os
import yaml

import shutil
from toolbox.config import get_config
from toolbox.file_manipulation.file import File
from main.data.cvat import CvatExport

# get_config() => to be fixed


if __name__ == "__main__":
    data_set = "hurricanes_2"

    conf = get_config()
    data_set_path = os.path.join(conf.data_annotated, data_set)

    file_names = os.listdir(data_set_path)
    files = [File(os.path.join(data_set_path, i)) for i in file_names]
    xml_files = {i.file_name: i for i in files if i.extension == ".xml"}
    images = {i.file_name: i for i in files if i.extension in [".jpg", ".png"]}
    to_delete = set(images.keys() - xml_files.keys())

    dest_path = os.path.join(conf.data_annotated_transformed, data_set)
    shutil.copytree(data_set_path, dest_path)

    main_dset = CvatExport(dest_path)
    main_dset.to_jpg()

    with open(os.path.join(conf.data_annotated_transformed, "logger.yaml")) as f:
        logger = yaml.full_load(f)

    logger[data_set] = "done"
    with open(os.path.join(conf.data_annotated_transformed, "logger.yaml"), "w") as f:
        yaml.dump(logger, f)

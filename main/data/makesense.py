# get annotations from makespace

import os
import shutil

from toolbox.config import get_config
from toolbox.file_manipulation.file import File

from main.parameters.base import ParamLoader
from main.workflow.workspace import WorkSpace
from main.data.cvat import CvatExport

from main.data.util import DataTransformLogger

if __name__ == "__main__":

    conf = get_config()
    params = ParamLoader('8')
    ws = WorkSpace(params, reset=True)

    a = ws.params.data_sets
    a.remove("residential_areas")

    log = DataTransformLogger()

    for d_set in ws.params.data_sets:

        if log.content.get(d_set) != "done":

            data_set_path = os.path.join(conf.data_annotated, d_set)
            dest_path = os.path.join(conf.data_annotated_transformed, d_set)

            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)

            file_names = os.listdir(data_set_path)
            files = [File(os.path.join(data_set_path, i)) for i in file_names]
            xml_files = {i.file_name: i for i in files if i.extension == ".xml"}
            images = {i.file_name: i for i in files if i.extension in [".jpg", ".png"]}
            to_delete = set(images.keys() - xml_files.keys())
            shutil.copytree(data_set_path, dest_path)

            main_dset = CvatExport(dest_path)
            main_dset.to_jpg()

            log.content[d_set] = "done"
            log.save()

            print("TRANSFORMED:", d_set)

        else:
            print("NOT TRANSFORMING:", d_set, "- already done!")

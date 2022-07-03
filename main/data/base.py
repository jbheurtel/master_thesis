import os

import yaml

from toolbox.config import get_config

from main.data.cvat import CvatExport, transform_dataset
from main.data.util import zipfolder
from main.parameters.base import ParamLoader
from main.workflow.workspace import WorkSpace


if __name__ == '__main__':

    conf = get_config()
    params = ParamLoader('10')
    ws = WorkSpace(params, reset=True)

    for d_set in ws.params.data_sets:
        transform_dataset(d_set)
    ws.import_data()
    main_cvat_dset = CvatExport(ws.p.data_imports)
    main_cvat_dset.reindex()
    print(main_cvat_dset.get_label_summary())
    main_cvat_dset.remap_labels(ws.params["label_map_dict"])
    print(main_cvat_dset.get_label_summary())
    main_cvat_dset.save_label_map()
    main_cvat_dset.split_data(**ws.params["split_params"])
    main_cvat_dset.move_splits(ws.p.data_transformed)

    gdrive_path_fldr = os.path.join(r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data", ws.name)
    gdrive_path_zip = gdrive_path_fldr + ".zip"

    if os.path.exists(gdrive_path_zip):
        os.remove(gdrive_path_zip)
    zipfolder(gdrive_path_fldr, ws.p.data_transformed)

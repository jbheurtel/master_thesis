import os

from toolbox.config import get_config

from main.data.cvat import CvatExport
from main.data.util import zipfolder
from main.parameters.base import ParamLoader
from main.workflow.workspace import WorkSpace


if __name__ == '__main__':

    conf = get_config()
    params = ParamLoader('1')
    ws = WorkSpace(params, reset=True)
    ws.import_data()

    for d_set in ws.params.data_sets:
        cvat_dset = CvatExport(os.path.join(ws.p.data_imports, d_set))
        cvat_dset.move(ws.p.data_transformed)
        cvat_dset.split_annotations()
        cvat_dset.to_jpg()

        for file in cvat_dset.files:
            file.move(ws.p.data_transformed)
        cvat_dset.delete()

    main_cvat_dset = CvatExport(ws.p.data_transformed)
    main_cvat_dset.reindex()
    main_cvat_dset.remap_labels(ws.params["label_map_dict"])
    main_cvat_dset.split_data(**ws.params["split_params"])

    os.remove(r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data.zip")
    zipfolder(r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data", ws.p.data_transformed)


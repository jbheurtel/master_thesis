from main.model.detection import get_detections_from_xml
from toolbox.file_manipulation.file import XmlFile, File

from toolbox.config import get_config

import os


if __name__ == '__main__':

    conf = get_config()
    main = r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data/full_lgrain_8T2V/validate"

    all_paths = [os.path.join(main, i) for i in os.listdir(main)]
    all_xml = [i for i in all_paths if File(i).extension == ".xml"]


    def group_detections(detections):
        dx = dict()
        for i in detections:
            if i.name not in dx.keys():
                dx[i.name] = 1
            else:
                dx[i.name] += 1
        return dx


    dxall = dict()
    for i in all_xml:
        xml_file = XmlFile(i)
        detections = get_detections_from_xml(xml_file=xml_file)
        dx = group_detections(detections)

        for k, v in dx.items():
            if k not in dxall.keys():
                dxall[k] = v
            else:
                dxall[k] += v


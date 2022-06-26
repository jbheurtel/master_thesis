import os

import numpy as np
from PIL import Image

from main.parameters.base import ParamLoader
from main.model.visuals.shapes import DetectionSet, summarise_groups, get_detections_from_xml
from main.model.visuals.vis import visualize

from toolbox.file_manipulation.file import XmlFile, File
from toolbox.config import get_config




if __name__ == '__main__':

    conf = get_config()
    main = os.path.join(conf.data_annotated, "hurricanes_2")

    all_paths = [os.path.join(main, i) for i in os.listdir(main)]
    all_xml = [i for i in all_paths if File(i).extension == ".xml"]

    XML_PATH = all_xml[2]

    xml_file = XmlFile(XML_PATH)
    image_path = XML_PATH.replace(".xml", ".png")
    detections = get_detections_from_xml(xml_file=xml_file)

    conf = get_config()
    params = ParamLoader('6')

    for d in detections:
        d.relabel(params.label_map_dict)

    image = Image.open(image_path).convert('RGB')
    image_np_1 = np.asarray(image)
    image_np = visualize(image_np_1, detections)

    image = Image.fromarray(image_np)
    image.show()

    DX = DetectionSet(detections)
    DX.get_unique_names()
    DX.summarise()
    groups = DX.form_groups()
    groups_summary = summarise_groups(groups)
    for i in groups_summary:
        print(i)

import os

from main.parameters.base import ParamLoader
from main.model.visuals.shapes import Detection, DetectionSet, summarise_groups

from toolbox.config import get_config
from toolbox.file_manipulation.file import XmlFile, File


def get_detections_from_xml(xml_file: XmlFile):
    infos = xml_file.open()
    detections = list()

    if isinstance(infos["annotation"]["object"], list):
        objects = infos["annotation"]["object"]
    else:
        objects = [infos["annotations"]["object"]]

    for i in objects:
        left = int(i["bndbox"]["xmin"])
        right = int(i["bndbox"]["xmax"])
        top = int(i["bndbox"]["ymax"])
        bottom = int(i["bndbox"]["ymin"])
        name = i["name"]
        score = 1
        detection = Detection(left, right, top, bottom, name, score)
        detections.append(detection)
    return detections


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

    from main.model.tf_od.vis import visualize
    from PIL import Image
    import numpy as np

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

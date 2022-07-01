import os

from main.model.detection import get_detections_from_xml

from toolbox.file_manipulation.file import XmlFile, File
from toolbox.config import get_config
from PIL import Image



import dicttoxml


def get_tiny_detections(xml: XmlFile, img: File):

    image = Image.open(img.path)
    w, h = image.width, image.height
    img_pixels = w*h

    detections = get_detections_from_xml(xml)
    detections_areas = {i: i.area for i in detections}
    detections_proportions = {k: v/img_pixels for k, v in detections_areas.items()}

    threshold = 1e-5

    tiny_detections = {k: v for k, v in detections_proportions.items() if v < threshold}

    if len(tiny_detections) != 0:
        print("img: " + img.file_name + " has " + str(len(tiny_detections)) + " unusually small detections")

    return tiny_detections


def eliminate_tiny_detections(path):
    files = os.listdir(path)
    paths = [os.path.join(path, i) for i in files]
    xml_paths = [i for i in paths if File(i).extension == ".xml"]
    xml_paths.sort()

    sets = [((XmlFile(i)), File(i.replace(".xml", ".png"))) for i in xml_paths]

    for xml, img in sets:

        detections = get_tiny_detections(xml, img)

        if len(detections) != 0:
            xml.delete()
            img.delete()
            print("deleting: " + img.file_name)

if __name__ == "__main__":
    conf = get_config()
    data_path = conf.data_annotated
    image_folders = os.listdir(data_path)
    image_folders = [i for i in image_folders if "." not in i]
    image_folder_paths = [os.path.join(data_path, i) for i in image_folders]

    for p in image_folder_paths:
        if "annotations.xml" not in os.listdir(p):
            eliminate_tiny_detections(p)
            print(os.path.basename(p))
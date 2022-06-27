import os

from main.model.detection import get_detections_from_xml

from toolbox.file_manipulation.file import XmlFile, File
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


if __name__ == "__main__":

    base_folder = r"/Users/jean-baptisteheurtel/Desktop/hurricanes_2/train"
    files = os.listdir(base_folder)
    paths = [os.path.join(base_folder, i) for i in files]
    xml_paths = [i for i in paths if File(i).extension == ".xml"]
    xml_paths.sort()

    sets = [((XmlFile(i)), File(i.replace(".xml", ".jpg"))) for i in xml_paths]

    for xml, img in sets:

        detections = get_tiny_detections(xml, img)

        if len(detections) != 0:
            xml.delete()
            img.delete()
            print("deleting: " + img.file_name)

        # TODO: tried to get rid of box that was too small, but the list in dict values doesnt get converted as i wish.
        # if len(detections) != 0:
        #     xml_dict = xml.open()
        #
        #     old_object_value = xml_dict["annotation"]["object"]
        #     new_object_value = list()
        #     for det in detections:
        #         for box in old_object_value:
        #             coordinates = (int(box["bndbox"]["xmax"]),  int(box["bndbox"]["xmin"]),
        #                            int(box["bndbox"]["ymax"]), int(box["bndbox"]["ymin"]))
        #             print(coordinates)
        #             print(det.box)
        #             if coordinates != det.box:
        #                 new_object_value.append(box)
        #             else:
        #                 print("removing a box")
        #
        #     xml_dict["annotation"]["object"] = new_object_value
        #
        #     from dicttoxml import dicttoxml
        #     from xml.dom.minidom import parseString
        #
        #     xml_text = dicttoxml(xml_dict, attr_type=False, root=False).decode()
        #     xml_text = parseString(xml_text).toprettyxml()
        #     f = open(xml.path, "w")
        #     f.write(xml_text)
        #     f.close()

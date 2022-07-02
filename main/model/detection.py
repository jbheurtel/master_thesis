import os
from typing import List

import numpy as np
import pandas as pd
import cv2
from PIL import Image
from shapely.geometry import Polygon

from main.parameters.base import ParamLoader

from toolbox.file_manipulation.file import XmlFile, File
from toolbox.config import get_config

_COLOR_PALETTE = {
    "house": (0, 255, 0),
    "flooded_house": (0, 128, 255),
    "damage": (255, 0, 0),
    "destroyed_house": (64, 64, 64),
    "roof_destruction": (255, 0, 0),
    "roof_damage": (255, 128, 0),
    "wall_damage": (128, 0, 255),
    "wall_destruction": (255, 0, 0)
}

STRUCTURES = ["house", "destroyed_house", "flooded_house"]
DAMAGES = ["roof_destruction", "damage", "roof_damage", "wall_damage", "wall_destruction", "total_destruction"]


class Detection:
    def __init__(self, left, right, top, bottom, name, score):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.name = name
        self.score = score
        self.box = (left, right, top, bottom)
        self.shape = Polygon([(left, bottom), (right, bottom), (right, top), (left, top)])
        self.area = self.shape.area

    def relabel(self, relabel_dictionary):
        for k, v in relabel_dictionary.items():
            if k == self.name:
                self.name = v

    def resize(self, factor):
        self.__init__(
            left=round(self.left * factor),
            right=round(self.right * factor),
            top=round(self.top * factor),
            bottom=round(self.bottom * factor),
            name=self.name,
            score=self.score
        )


def multi_area(shapes):
    dmg = shapes[0]
    for i in shapes:
        dmg = dmg.union(i)
    return dmg.area


class DamageGroup:
    def __init__(self, groups):
        self.groups = groups

    def summarise_groups(self, group_by=None):

        assert group_by in [None, "damage", "damage_type"]

        summary_dict = dict()
        for k, v in self.groups.items():
            summary = dict()
            summary["item"] = k.name
            summary["area"] = k.area
            summary["score"] = round(k.score, 2)
            summary["damage_prop"] = 0 if k.name == "house" else 1
            damages = []
            for i in v:
                damage = dict()
                damage["obj"] = i
                damage["name"] = i.name
                damage["area"] = i.area
                damage["score"] = round(i.score, 4)
                damage["area_prop"] = round(i.area / summary["area"], 4)
                damages.append(damage)
            summary["damages"] = damages
            summary_dict[k] = summary

        if group_by:
            for k, v in summary_dict.items():

                groups = dict()
                if group_by == "damage":
                    groups["damages"] = [dmg["obj"].shape for dmg in v["damages"]]
                elif group_by == "damage_type":
                    for dmg in v["damages"]:
                        dmg_type = dmg["name"]
                        if dmg_type not in groups.keys():
                            groups[dmg_type] = list()
                        groups[dmg_type].append(dmg["obj"].shape)

                del summary_dict[k]["damage_prop"]
                del summary_dict[k]["damages"]

                for grp_name, grp_members in groups.items():
                    if v:
                        area = round(multi_area(grp_members)/v["area"], 4)
                    else:
                        area = 0
                    v[grp_name] = area
                    summary_dict[k] = v

        else:
            for k, v in summary_dict.items():
                damages = [dmg["obj"].shape for dmg in v["damages"]]
                if damages:
                    damages_area = multi_area(damages)
                    area_prop = round(damages_area / v["area"], 4)
                else:
                    area_prop = 0

                summary_dict[k]["damage_prop"] = area_prop
        return summary_dict




    #
    # def summarise_by(self, damage_type="damage"):
    #
    #         summary_dict = self.summarise_groups()
    #
    #         if damage_type == "damages":
    #             groups["damages"] = summary["damages"]
    #         else:
    #             for k, v in groups["damages"].items():
    #                 if v["name"] not in groups.keys():
    #                     groups[v["name"]] = list()
    #                 groups[v["name"]].append(v)
    #
    #         if group:
    #             def summarise_group(group):
    #                 dmg = group[0]["obj"].shape
    #                 for i in group:
    #                     dmg = dmg.union(i["obj"].shape)
    #
    #                 summary["damage_prop"] = round(dmg.area / summary["area"], 4)
    #
    #         summary_dict[k] = summary
    #     return summary_dict


class DetectionSet:

    def __init__(self, detections: List[Detection]):
        self.items = detections

    def append(self, item):
        self.items.append(item)

    def summarise(self):
        summary = pd.DataFrame(index=[list(range(len(self.items)))], columns=["score", "name", "area"])
        for i in range(len(self.items)):
            summary.loc[i, :] = self.items[i].score, self.items[i].name, self.items[i].area
        return summary.sort_values("area", ascending=False)

    def get_unique_names(self):
        a = self.summarise()
        return a.groupby("name")["name"].count().to_dict()

    def form_groups(self):
        houses = []
        damages = []

        for i in self.items:
            if i.name in STRUCTURES:
                houses.append(i)
            elif i.name in DAMAGES:
                damages.append(i)

        groups = {h: [] for h in houses}
        for dmg in damages:
            candidates = {}
            for house in houses:
                i = dmg.shape.intersection(house.shape).area
                candidates[house] = i

            closest = max(candidates, key=candidates.get)
            if candidates[closest] / dmg.area > 0.5:
                groups[closest].append(dmg)

        return DamageGroup(groups)


def get_detections_from_xml(xml_file: XmlFile):
    infos = xml_file.open()
    detections = list()

    if isinstance(infos["annotation"]["object"], list):
        objects = infos["annotation"]["object"]
    else:
        objects = [infos["annotation"]["object"]]

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


def visualize(
        image: np.ndarray,
        detections: List[Detection],
        margin=5,
        row_size=15,
        font_size=2,
        font_thickness=2,
        rectangle_thickness=2
) -> np.ndarray:
    for detection in detections:
        # Draw bounding_box
        start_point = detection.left, detection.top
        end_point = detection.right, detection.bottom
        # area = '{:0.2e}'.format(detection.area)
        area = detection.area
        item = detection.name
        cv2.rectangle(image, start_point, end_point, _COLOR_PALETTE[item], rectangle_thickness)

        # Draw label and score
        class_name = detection.name
        probability = round(detection.score, 2)
        result_text = class_name + ' (p: ' + str(probability) + ", area: " + str(area) + ')'
        text_location = (margin + detection.right,
                         margin + row_size + detection.top)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, _COLOR_PALETTE[item], font_thickness)

    return image


if __name__ == '__main__':

    conf = get_config()
    main = os.path.join(conf.data_annotated, "hurricanes_2")

    all_paths = [os.path.join(main, i) for i in os.listdir(main)]
    all_xml = [i for i in all_paths if File(i).extension == ".xml"]

    XML_PATH = all_xml[15]

    xml_file = XmlFile(XML_PATH)
    image_path = XML_PATH.replace(".xml", ".png")
    detections = get_detections_from_xml(xml_file=xml_file)

    conf = get_config()
    params = ParamLoader('6')

    image = Image.open(image_path).convert('RGB')

    original_dims = (image.height, image.width)
    # image.thumbnail((512, 512), Image.ANTIALIAS)
    final_dims = (image.height, image.width)

    resize_factor = np.array((final_dims[0] / original_dims[0], final_dims[1] / original_dims[1])).mean()

    for d in detections:
        # d.relabel(params.label_map_dict)
        d.resize(resize_factor)

    image_np_1 = np.asarray(image)
    image_np = visualize(image_np_1, detections, rectangle_thickness=3)  # margin=5, font_size=0.5, font_thickness=1)

    image = Image.fromarray(image_np)
    image.show()

    DX = DetectionSet(detections)
    DX.get_unique_names()
    DX.summarise()
    groups = DX.form_groups()
    # groups.summarise_groups()
    # groups.summarise_groups("damage")
    res = groups.summarise_groups()
    for k, v in res.items():
        print(k, ":", v)

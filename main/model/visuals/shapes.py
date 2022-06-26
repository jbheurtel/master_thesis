import pandas as pd

from typing import List


class Detection:
    def __init__(self, left, right, top, bottom, name, score):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.name = name
        self.score = score
        self.area = self._area()
        self.box = (left, right, top, bottom)


    def _area(self):
        return (self.right - self.left)*(self.top - self.bottom)

    def intersect(self, shape_2):
        w = max(min(self.right, shape_2.right) - max(self.left, shape_2.left), 0)
        h = max(min(self.top, shape_2.top) - max(self.bottom, shape_2.bottom, 0), 0)
        return w * h

    def union(self, shape_2):
        return self.area + shape_2.area - self.intersect(shape_2)

    def relabel(self, relabel_dictionary):
        for k, v in relabel_dictionary.items():
            if k == self.name:
                self.name = v


class DetectionSet:

    def __init__(self, detections: List[Detection]):
        self.items = detections

    def append(self, item):
        self.items.append(item)

    def summarise(self):
        summary = pd.DataFrame(index=[list(range(len(self.items)))], columns=["score", "name", "area"])
        for i in range(len(self.items)):
            summary.loc[i,:] = self.items[i].score, self.items[i].name, self.items[i].area
        return summary.sort_values("area", ascending=False)

    def get_unique_names(self):
        a = self.summarise()
        return a.groupby("name")["name"].count().to_dict()

    def form_groups(self):
        houses = []
        damages = []

        for i in self.items:
            if i.name in ["house", "destroyed_house"]:
                houses.append(i)
            elif i.name in ["damage"]:
                damages.append(i)

        groups = {h: [] for h in houses}
        for dmg in damages:
            candidates = {}
            for house in houses:
                i = dmg.intersect(house)
                candidates[house] = i

            closest = max(candidates, key=candidates.get)
            if candidates[closest] / dmg.area <= 0.5:
                print("cannot securely allocate damage to house")
            else:
                groups[closest].append(dmg)

        return groups


def summarise_groups(groups):
    summary_list = list()
    for k, v in groups.items():
        summary = dict()
        summary["item"] = k.name
        summary["area"] = k.area
        summary["score"] = round(k.score, 2)
        summary["components"] = list()
        summary["damage_prop"] = 0
        for i in v:
            component = dict()
            component["name"] = i.name
            component["area"] = i.area
            component["score"] = round(i.score, 2)
            component["area_prop"] = round(i.area / summary["area"], 2)
            summary["components"].append(component)
            summary["damage_prop"] += round(i.area / summary["area"], 2)
        summary_list.append(summary)
    return summary_list


if __name__ == "__main__":

    all_detections = [
        (1, 5, 4, 1, "house", 0.84),
        (4, 8, 6, 3, "house", 0.34),
        (3, 6, 5, 3, "damage", 0.59),
        (1, 4, 3, 1, "damage", 0.94),
        (7, 10, 7, 5, "damage", 0.30)
    ]

    detections = DetectionSet([Detection(*i) for i in all_detections])

    detections.summarise()
    detections.get_unique_names()


import os
import shutil

from PIL import Image
from dict2xml import dict2xml
import pandas as pd
import yaml

import xmltodict


from main.data.util import fmt_proj

from toolbox.file_manipulation.file import File
from toolbox.config import get_config


class CvatExport:
    def __init__(self, path):

        # location info
        self.path = path
        self.dir = os.path.dirname(path)
        self.name = os.path.basename(path)

        # content info
        self.files = [File(os.path.join(self.path, i)) for i in os.listdir(self.path)]
        self.images = list(filter(lambda x: x.extension in [".jpg", ".png"], self.files))
        self.cvat_annotations = os.path.join(self.path, "annotations.xml")
        self.annotations = [i for i in self.files if i.extension == ".xml"]
        self.image_formats = set([i.extension for i in self.images])
        self._load_tf_images()

    def _load_tf_images(self):
        tf_images = list()
        for img in self.images:
            xml_counterpart = img.path.replace(img.extension, ".xml")
            if os.path.exists(xml_counterpart):
                tf_images.append(AnnotatedImageTF(img, File(xml_counterpart)))
        self.tf_images = tf_images

    def to_jpg(self):
        for f in self.tf_images:
            if not f.format == ".jpg":
                f.to_jpg()
        self.__init__(self.path)

    def move(self, dest):
        shutil.move(self.path, dest)
        path = os.path.join(os.path.join(dest, self.name))
        self.__init__(path)

    def delete(self):
        shutil.rmtree(self.path)

    def reindex(self):
        pictures_dict = pd.Series(self.tf_images).to_dict()
        pictures_dict = {v: "img_" + str(k) for k, v in pictures_dict.items()}

        for tf_image, new_name in pictures_dict.items():
            tf_image.rename(new_name)
        self.__init__(self.path)

    # TODO: integrate previous functions into this
    def remap_labels(self, label_map_dict):
        for tf_image in self.tf_images:
            with open(tf_image.annotations.path) as f:
                xml = f.read()
            for k, v in label_map_dict.items():
                xml = xml.replace("<name>" + k + "</name>", "<name>" + v + "</name>")
            # xml = xml.split("\n")
            with open(tf_image.annotations.path, "w") as f:
                f.write(xml)

        # join label maps:
        label_paths = [os.path.join(self.path, i) for i in os.listdir(self.path) if ".yaml" in i]
        final_labels = set()
        for i in label_paths:
            with open(i) as f:
                label_map = yaml.full_load(f)
            labels = label_map.values()
            for i in labels:
                if i in label_map_dict.keys():
                    final_labels = final_labels.union({label_map_dict[i]})
                else:
                    final_labels = final_labels.union({i})

        final_label_map = dict()
        for i in range(len(final_labels)):
            final_label_map[i] = list(final_labels)[i]

        for i in label_paths:
            os.remove(i)

        with open(os.path.join(self.path, "label_map.yaml"), "w") as f:
            yaml.dump(final_label_map, f)

    def split_annotations(self):

        xml_dict = CvatXmlParser(self.cvat_annotations).xml_dict

        common_img_info = dict()
        common_img_info["folder"] = os.path.basename(os.path.dirname(self.cvat_annotations))
        common_img_info["source"] = dict()
        common_img_info["source"]["database"] = 'Unknown'
        common_img_info["segmented"] = str(0)

        common_object_info = dict()
        common_object_info["pose"] = "Unspecified"
        common_object_info["truncated"] = 0
        common_object_info["difficult"] = 0

        labels = set()

        for image in xml_dict["annotations"]["image"]:

            # initialization
            image_file = File(os.path.join(self.path, image['@name']))
            annotation_path = image_file.path.replace(image_file.extension, ".xml")

            # building annotation for that image
            new_dict = dict()
            annotations = dict()
            for k, v in common_img_info.items():
                annotations[k] = v

            annotations["filename"] = image_file.base
            annotations["path"] = image_file.path
            annotations["size"] = dict()
            annotations["size"]["width"] = image['@width']
            annotations["size"]["height"] = image['@height']
            annotations["size"]["depth"] = str(3)

            # adding a box for each annotation
            if "box" in image.keys():
                objects = list()
                if isinstance(image["box"], list):
                    for box in image["box"]:
                        new_object = format_new_object(box, common_object_info)
                        objects.append(new_object)
                        labels = labels.union({new_object["name"]})
                elif isinstance(image["box"], dict):
                    new_object = format_new_object(image["box"], common_object_info)
                    objects.append(new_object)
                    labels = labels.union({new_object["name"]})
                else:
                    print("break")
                annotations["object"] = objects

            new_dict["annotation"] = annotations

            # saving the annotation
            xml = dict2xml(new_dict)
            with open(annotation_path, "w") as f:
                f.write(xml)
                f.close()

        # saving the label info
        labels = pd.Series(list(labels)).to_dict()
        with open(os.path.join(self.path, "labels.yaml"), "w") as f:
            yaml.dump(labels, f)

        self.__init__(self.path)

    def get_label_summary(self):
        all_labels = dict()
        xmls = self.annotations
        xml_paths = [i.path for i in xmls]
        for i in xml_paths:
            labels = get_labels_from_xml(i)

            for k, v in labels.items():
                if k not in all_labels.keys():
                    all_labels[k] = v
                else:
                    all_labels[k] += v
        return all_labels

    def save_label_map(self):
        labels = self.get_label_summary()
        label_map = {i : list(labels.keys())[i] for i in range(len(labels))}

        with open(os.path.join(self.path, "label_map.yaml"), "w") as f:
            yaml.dump(label_map, f)

    def split_data(self, train=1, test=0, validation=0):

        split_params = {"train": train, "test": test, "validation": validation}
        split_params = {k: v/sum(split_params.values()) for k, v in split_params.items()}

        df = pd.Series(self.tf_images).sample(frac=1).reset_index(drop=True)
        n_train = round(len(df) * split_params["train"])
        n_test = round(len(df) * split_params["test"])
        n_val = round(len(df) * split_params["validation"])

        imgs_set = dict()
        imgs_set["train"] = list(df.iloc[0:n_train].values)
        imgs_set["test"] = list(df.iloc[n_train:(n_train + n_test)].values)
        imgs_set["validate"] = list(df.iloc[(n_train + n_test): (n_train + n_test + n_val)].values)

        for k, v in imgs_set.items():
            data_group_path = os.path.join(self.path, k)
            os.mkdir(data_group_path)
            for tf_image in v:
                tf_image.move(data_group_path)

    def move_splits(self, dest_fldr):
        for folder in ["train", "test", "validate", "label_map.yaml"]:
            source = os.path.join(self.path, folder)
            dest = os.path.join(dest_fldr, folder)
            shutil.move(source, dest)


def png_to_jpg(file: File):
    new_path = file.path.replace(".png", ".jpg")
    im = Image.open(file.path)
    rgb_im = im.convert('RGB')
    rgb_im.save(new_path)
    file.delete()


def replace_in_xml(file: File, replace_dict: dict):
    # replace the pngs to jpegs
    with open(file.path) as f:
        xml = f.readlines()

    for k, v in replace_dict.items():
        xml = "".join(xml).replace(k, v).split("\n")

    with open(file.path, "w") as f:
        for line in xml:
            f.write(line)
            f.write("\n")


# CvatXMLParser
class CvatXmlParser:
    def __init__(self, path_to_xml):
        self.fpath = path_to_xml
        self.xml = _load(self.fpath)
        self.xml_dict = _file_to_dict(self.xml)


def _load(fpath):
    with open(fpath, 'r', encoding='utf-8') as file:
        return file.read()


def _file_to_dict(xml_file):
    return xmltodict.parse(xml_file)


def format_new_object(box, common_object_info):
    new_object = dict()
    for k, v in common_object_info.items():
        new_object[k] = v

    new_object["name"] = fmt_proj(box['@label'])
    bndbox = dict()
    bndbox["xmin"] = str(round(float(box['@xtl'])))
    bndbox["ymin"] = str(round(float(box['@ytl'])))
    bndbox["xmax"] = str(round(float(box['@xbr'])))
    bndbox["ymax"] = str(round(float(box['@ybr'])))
    new_object["bndbox"] = bndbox

    return new_object


class AnnotatedImageTF:
    def __init__(self, img: File, xml: File):
        self.img = img
        self.annotations = xml
        self.format = self.img.extension

    def move(self, dir):
        self.img.move(dir)
        self.annotations.move(dir)

    def delete(self):
        self.img.delete()
        self.annotations.delete()

    def rename(self, new_name):
        replace_in_xml(self.annotations, {self.img.file_name: new_name})
        self.img.rename(new_name)
        self.annotations.rename(new_name)

    def to_jpg(self):
        png_to_jpg(self.img)
        replace_in_xml(self.annotations, {self.img.extension: ".jpg"})


def transform_dataset(d_set):
    conf = get_config()

    data_source = conf["data_annotated"]
    data_dest = conf["data_annotated_transformed"]

    with open(os.path.join(data_dest, "logger.yaml")) as f:
        logger = yaml.full_load(f)

        if logger.get(d_set) != "done":
            print("transforming: " + d_set)
            cvat_dset = CvatExport(os.path.join(data_source, d_set))
            cvat_dset.move(data_dest)
            cvat_dset.split_annotations()
            cvat_dset.to_jpg()

            logger[d_set] = "done"
            with open(os.path.join(data_dest, "logger.yaml"), "w") as f:
                yaml.dump(logger, f)
        else:
            print("not transforming: " + d_set, " - already done")


def get_labels_from_xml(xml_path):

    fileptr = open(xml_path, "r")

    xml_content = fileptr.read()
    my_ordered_dict = xmltodict.parse(xml_content)

    labels = dict()

    object = my_ordered_dict["annotation"]["object"]
    objects = object if isinstance(object, list) else [object]

    for i in objects:
        if i["name"] not in labels.keys():
            labels[i["name"]] = 1
        else:
            labels[i["name"]] += 1

    return labels

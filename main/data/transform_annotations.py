import shutil
import zipfile
import yaml
import os

from PIL import Image
import pandas as pd
import xmltodict

from dict2xml import dict2xml
from main.data.util import fmt_proj


def _load(fpath):
    with open(fpath, 'r', encoding='utf-8') as file:
        return file.read()


def _file_to_dict(xml_file):
    return xmltodict.parse(xml_file)


class CvatXmlParser:
    def __init__(self, path_to_xml):
        self.fpath = path_to_xml
        self.xml = _load(self.fpath)
        self.xml_dict = _file_to_dict(self.xml)


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


def prepare_cvat_folder(fldr_path):
    annotations_path = os.path.join(fldr_path, "annotations.xml")

    a = CvatXmlParser(annotations_path)
    xml_dict = a.xml_dict

    common_img_info = dict()
    common_img_info["folder"] = os.path.basename(os.path.dirname(annotations_path))
    common_img_info["source"] = dict()
    common_img_info["source"]["database"] = 'Unknown'
    common_img_info["segmented"] = str(0)

    common_object_info = dict()
    common_object_info["pose"] = "Unspecified"
    common_object_info["truncated"] = 0
    common_object_info["difficult"] = 0

    labels = set()

    for image in xml_dict["annotations"]["image"]:
        new_dict = dict()
        annotations = dict()
        for k, v in common_img_info.items():
            annotations[k] = v

        annotations["filename"] = image['@name']
        annotations["path"] = os.path.join(fldr_path, image['@name'])
        annotations["size"] = dict()
        annotations["size"]["width"] = image['@width']
        annotations["size"]["height"] = image['@height']
        annotations["size"]["height"] = str(3)

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

        xml = dict2xml(new_dict)
        new_path = annotations["path"].replace(".png", ".xml")
        with open(new_path, "w") as f:
            f.write(xml)
            f.close()

    labels = pd.Series(list(labels)).to_dict()
    with open(os.path.join(fldr_path, "labels.yaml"), "w") as f:
        yaml.dump(labels, f)


def copy_files(src, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)

    for file in os.listdir(src):
        if file != "annotations.xml":
            old_file = os.path.join(src, file)
            if ".xml" in file:
                new_file = os.path.join(dest, file)
                shutil.copyfile(old_file, new_file)
            elif ".png" in file:
                new_file = os.path.join(dest, file.replace(".png", ".jpg"))
                im = Image.open(old_file)
                rgb_im = im.convert('RGB')
                rgb_im.save(new_file)


def reindex_files_and_annotations(main):
    pictures = [file for file in os.listdir(main) if ".jpg" in file]
    pictures_dict = pd.Series(pictures).to_dict()
    pictures_dict = {v: "img_" + str(k) + ".jpg" for k, v in pictures_dict.items()}
    for k, v in pictures_dict.items():
        old_name = os.path.join(main, k)
        new_name = os.path.join(main, v)
        old_xml_path = os.path.join(main, k.replace(".jpg", ".xml"))
        new_xml_path = os.path.join(main, v.replace(".jpg", ".xml"))
        os.rename(old_name, new_name)

        with open(old_xml_path) as f:
            xml = f.readlines()
        xml = "".join(xml).replace(k.replace(".jpg", ".png"), v).split("\n")

        with open(new_xml_path, "w") as f:
            for line in xml:
                f.write(line)
                f.write("\n")
        os.remove(old_xml_path)


# def refactor_annotations(main):


def split_data(src, dest, train, test, val):
    if not os.path.exists(dest):
        os.makedirs(dest)

    assert train + test + val == 1
    pictures = [file for file in os.listdir(src) if ".jpg" in file]
    import pandas as pd
    df = pd.Series(pictures).sample(frac=1).reset_index(drop=True)
    n = len(pictures)
    n_train = round(n * train)
    n_test = round(n * test)
    n_val = round(n * val)

    imgs_set = dict()
    imgs_set["train"] = list(df.iloc[0:n_train].values)
    imgs_set["test"] = list(df.iloc[n_train:n_test].values)
    imgs_set["validate"] = list(df.iloc[n_train + n_test: n_train + n_test + n_val].values)

    for k, v in imgs_set.items():
        fldr_path = os.path.join(dest, k)
        if not os.path.exists(fldr_path):
            os.mkdir(fldr_path)
        for img in v:
            old_img_path = os.path.join(src, img)
            new_img_path = os.path.join(fldr_path, img)
            old_xml_path = os.path.join(src, img.replace(".jpg", ".xml"))
            new_xml_path = os.path.join(fldr_path, img.replace(".jpg", ".xml"))
            shutil.copyfile(old_img_path, new_img_path)
            shutil.copyfile(old_xml_path, new_xml_path)


def copy_labeL_maps(raw, main):
    label_map_values = set()
    for img_set in os.listdir(raw):
        if "." not in img_set:
            with open(os.path.join(raw, img_set, "labels.yaml")) as f:
                labels = yaml.full_load(f)
                label_map_values = label_map_values.union(set(labels.values()))

    label_map = dict()
    for i in range(len(label_map_values)):
        label_map[str(i)] = list(label_map_values)[i]

    with open(os.path.join(main, "label_map.yaml"), "w") as f:
        yaml.dump(label_map, f)


def remap_labels(main, remap_dict: dict):
    # remap xml files
    xml_files = [i for i in os.listdir(main) if ".xml" in i]
    for xml_file in xml_files:
        xml_file_path = os.path.join(main, xml_file)
        with open(xml_file_path) as f:
            xml = f.readlines()

        xml = "".join(xml)
        for k, v in remap_dict.items():
            xml = xml.replace(k, v)
        xml = xml.split("\n")

        with open(xml_file_path, "w") as f:
            for line in xml:
                f.write(line)
                f.write("\n")

    # remap label map
    label_map_path = os.path.join(main, "label_map.yaml")
    with open(label_map_path) as f:
        label_map = yaml.full_load(f)

    new_label_map = dict()
    for k, v in label_map.items():
        if v in remap_dict.keys():
            new_label_map[k] = remap_dict[v]
        else:
            new_label_map[k] = v

    new_reduced_label_map = dict()
    label_map_values = set(new_label_map.values())
    for i in range(len(label_map_values)):
        new_reduced_label_map[i] = list(label_map_values)[i]

    with open(label_map_path, "w") as f:
        yaml.dump(new_reduced_label_map, f)


# compress and copy to gdrive
def zipfolder(foldername, target_dir):
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])


if __name__ == '__main__':

    data_fldr = r"/Users/jean-baptisteheurtel/Main/university/masters/Thesis/07_Experiments/tf_lite/own_case/data"

    raw = os.path.join(data_fldr, "cvat")
    main = os.path.join(data_fldr, "main")
    final = os.path.join(data_fldr, "ready")

    remap_dict = {
        "non_flooded": "house",
        "flooded_severe": "house",
        "flooded_mild": "house"
    }

    for img_set in os.listdir(raw):
        if "." not in img_set:
            img_set_path = os.path.join(raw, img_set)
            prepare_cvat_folder(img_set_path)
            copy_files(img_set_path, main)

    reindex_files_and_annotations(main)
    copy_labeL_maps(raw, main)
    remap_labels(main=main, remap_dict=remap_dict)
    split_data(main, final, train=0.8, test=0, val=0.2)
    shutil.copyfile(os.path.join(main, "label_map.yaml"), os.path.join(final, "label_map.yaml"))
    os.remove(r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data.zip")
    zipfolder(r"/Volumes/GoogleDrive/My Drive/03_University/MasterThesis/data", final)

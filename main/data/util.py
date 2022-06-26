import zipfile
import os

import xmltodict


def fmt_proj(s: str):
    ix = s.rfind(".")
    if ix != -1:
        extension = s[ix:]
    else:
        extension = ""

    ns = s.replace(extension, "")
    ns = ns.replace(" ", "_")
    ns = ns.replace("-", "")
    ns = ns.lower()
    ns = ns.replace(".", "")

    ns = ns.replace("(", "")
    ns = ns.replace(")", "")

    if extension == ".png":
        ns = ns.replace("_at_", "_")
        ns = ns.replace("screen_shot_", "")

    return ns + extension


def zipfolder(source, dest):
    zipobj = zipfile.ZipFile(source + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(dest) + 1
    for base, dirs, files in os.walk(dest):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])


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


def get_label_summary(xml_file_paths: list):
    all_labels = dict()
    for i in xml_file_paths:
        labels = get_labels_from_xml(i)

        for k, v in labels.items():
            if k not in all_labels.keys():
                all_labels[k] = v
            else:
                all_labels[k] += v
    return all_labels


from toolbox.util import Map

from main.data.util import fmt_proj


def parse_img(img):
    proj_name = fmt_proj(img["@name"])

    d_image = Map()
    d_image["properties"] = Map()
    d_image.properties.raw_name = img["@name"]
    d_image.properties.w = img["@width"]
    d_image.properties.h = img["@height"]

    d_image["objects"] = Map()
    d_image.objects.labels = list()
    d_image.objects.xmins = list()
    d_image.objects.xmaxs = list()
    d_image.objects.ymins = list()
    d_image.objects.ymaxs = list()

    if 'box' in img.keys():
        box = img["box"]

        if type(box) == list:
            for b in box:
                d_image.objects.labels.append(fmt_proj(b["@label"]))
                d_image.objects.xmins.append(fmt_proj(b['@xtl']))
                d_image.objects.xmaxs.append(fmt_proj(b["@xbr"]))
                d_image.objects.ymins.append(fmt_proj(b["@ytl"]))
                d_image.objects.ymaxs.append(fmt_proj(b["@ybr"]))

        elif type(box) == dict:
            d_image.objects.labels.append(fmt_proj(box["@label"]))
            d_image.objects.xmins.append(fmt_proj(box['@xtl']))
            d_image.objects.xmaxs.append(fmt_proj(box["@xbr"]))
            d_image.objects.ymins.append(fmt_proj(box["@ytl"]))
            d_image.objects.ymaxs.append(fmt_proj(box["@ybr"]))
        else:
            exit("unknown format")

    return proj_name, d_image


def get_labels(xml_dict):
    xml_labels = xml_dict["annotations"]["meta"]["task"]["labels"]
    out_labels = dict()
    count = 0
    for v in xml_labels.values():
        if type(v) == list:
            for e in v:
                out_labels[count] = fmt_proj(e["name"])
                count = count + 1
        else:
            out_labels[count] = fmt_proj(v["name"])
            count = count + 1
    return out_labels


def parse_all_imgs(xml_dict):
    output = Map()
    for img in xml_dict["annotations"]["image"]:
        name, res = parse_img(img)
        output[name] = res
    return output


def _load(fpath):
    with open(fpath, 'r', encoding='utf-8') as file:
        return file.read()


def _file_to_dict(xml_file):
    return xmltodict.parse(xml_file)


# parser
def _parse_xml_dict(xml_dict):
    res = Map()
    res["labels"] = get_labels(xml_dict)
    res["images"] = parse_all_imgs(xml_dict)
    return res


class CvatXmlParser:
    def __init__(self, path_to_xml):
        self.fpath = path_to_xml
        self.xml = _load(self.fpath)
        self.xml_dict = _file_to_dict(self.xml)
        self.parsed = _parse_xml_dict(self.xml_dict)

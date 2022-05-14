import os
import xmltodict


def rename_screenshot(name):
    new_name = name.replace('Screen Shot ', '')
    new_name = new_name.replace('.', '_')
    new_name = new_name.replace(' at ', '_')
    new_name = new_name.replace('-', '_')
    ix = new_name.rfind("_")
    new_name = new_name[:ix] + "." + new_name[ix + 1:]
    return new_name


def build_labels_from_xml(xml_path, destination_folder):
    with open(xml_path, 'r', encoding='utf-8') as file:
        my_xml = file.read()
    my_dict = xmltodict.parse(my_xml)

    output = list()
    for image in my_dict["annotations"]["image"]:
        name = image["@name"]
        list_coordinates = list()
        if "box" in image.keys():
            if isinstance(image["box"], dict):
                box = image["box"]
                coordinates = box['@xtl'], box['@ytl'], box['@xbr'], box['@ybr']
                coordinates = list(map(lambda x: str(round(float(x))), coordinates))
                coordinates = " ".join(coordinates)
                list_coordinates.append(coordinates)
            else:
                for box in image["box"]:
                    if isinstance(box, dict):
                        coordinates = box['@xtl'], box['@ytl'], box['@xbr'], box['@ybr']
                        coordinates = list(map(lambda x: str(round(float(x))), coordinates))
                        coordinates = " ".join(coordinates)
                    else:
                        coordinates = ""
                    list_coordinates.append(coordinates)
            count = len(list_coordinates)
        else:
            count = 0
            list_coordinates = ""

        txt_output = "  ".join(list_coordinates)
        name = os.path.join("positive", name)
        output.append(name + "  " + str(count) + "  " + txt_output)

    txt_file = os.path.join(destination_folder, 'info.txt')
    with open(txt_file, 'a') as f:
        f.writelines('\n'.join(output))



import os
import shutil

from main.data.prep.code_xml_to_csv import xml_to_csv
from main.data.util import fmt_proj
from main.data.__init__ import __version__

from toolbox.config import get_config
from toolbox.logger import TxTLogger


# 0. Transform main data by renaming and building a csv full of it.

def transform_annotated_data():
    # 0.1 configurations
    conf = get_config()
    raws_p = conf.data.annotated
    out_p = os.path.join(conf.data.annotated_transformed, __version__)
    img_groups = [x for x in os.listdir(raws_p) if not x.startswith('.')]

    # 0.2 set up data version folder
    if not os.path.exists(out_p):
        os.mkdir(out_p)

    # 1. getting the annotated data
    log = TxTLogger(out_p)
    tasks = set(img_groups) - set(log.to_dict()["done"])
    for img_group in tasks:
        input_dir = os.path.join(raws_p, img_group)
        output_dir = os.path.join(out_p, img_group)
        load_images(input_dir=input_dir, output_dir=output_dir)
        log.update("done", img_group)


def load_images(input_dir, output_dir):
    xml_path = os.path.join(input_dir, "annotations.xml")
    xml_df = xml_to_csv(xml_path)
    imgs = set(xml_df.filename)

    new_names = {i: fmt_proj(i) for i in xml_df.filename}
    xml_df.filename = xml_df.filename.apply(lambda x: new_names[x])

    os.mkdir(output_dir)
    csv_path = os.path.join(output_dir, "annotations.csv")
    xml_df.to_csv(csv_path, index=None)

    for img in imgs:
        scr = os.path.join(input_dir, img)
        dest = os.path.join(output_dir, new_names[img])
        shutil.copyfile(scr, dest)


if __name__ == "__main__":
    transform_annotated_data()

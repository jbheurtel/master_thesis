import os
import pandas as pd
import shutil
import tensorflow as tf
import yaml

from main.data.code_csv_to_tfrecords import create_tf_example
from main.data.__init__ import __version__

from main.workflow.workspace import WorkSpace
from main.parameters.base import ParamLoader

from toolbox.config import get_config


def load_data_to_workspace(ws: WorkSpace):
    conf = ws.get_config()
    main_paths = get_config()

    # 1. Load Annotations
    ants = load_annotations(main_data_fldr=main_paths["data"]["annotated_transformed"],
                            img_groups=conf["params"]["data_sets"])

    ants_path = os.path.join(conf["paths"]["data"]["root"], "annotations.csv")
    ants.to_csv(ants_path)

    # 2. Refactor, if needed
    if conf["params"]["group_flooded"]:
        refactor_annotations(ants_path)

    # 3. Build Label Map
    label_map = build_label_map(annotations=ants)

    label_map_path = os.path.join(conf["paths"]["data"]["root"], "label_map.yaml")
    with open(label_map_path, "w") as file:
        yaml.dump(label_map, file)

    label_map_path = label_map_path.replace(".yaml", ".pbtxt")
    to_pbtxt(label_map=label_map, label_map_path=label_map_path)

    # 4. Build Records
    build_tf_records(annotations=ants,
                     data_fldr=conf["paths"]["data"]["root"],
                     images_source_fldr=main_paths["data"]["annotated_transformed"],
                     split_params=conf["params"]["split_params"],
                     label_map=label_map)

    data_conf = dict()
    data_conf["label_map"] = label_map
    conf["data"] = data_conf
    ws.save_configs(conf)


def load_annotations(main_data_fldr, img_groups):
    df_ants = pd.DataFrame()
    for img_group in img_groups:
        path = os.path.join(main_data_fldr, __version__, img_group, "annotations.csv")
        annoations = pd.read_csv(path)
        df_ants = pd.concat([df_ants, annoations])
        df_ants = df_ants.reset_index(drop=True)
    return df_ants


def refactor_annotations(annotations_path):
    group_dict = {"flooded_severe": "flooded",
                  "flooded_mild": "flooded",
                  "non_flooded": "non_flooded"}

    annotations = pd.read_csv(annotations_path)
    col_annot = annotations["class"]
    col_annot = col_annot.apply(lambda x: str([group_dict[i] for i in eval(x)]))
    annotations["class"] = col_annot
    annotations.to_csv(annotations_path)


def build_label_map(annotations):
    label_map = dict()
    classes = annotations["class"].to_list()
    classes = [eval(x) for x in classes]
    classes = set([item for sublist in classes for item in sublist])
    count = 0
    for i in classes:
        label_map[i] = count
        count = count + 1
    return label_map


def build_tf_records(annotations, data_fldr, images_source_fldr, split_params: dict, label_map):
    n = len(annotations)

    n_train, n_val, n_test = (n * split_params["train"], n * split_params["validation"], n * split_params["test"])
    df_ants = annotations.sample(frac=1)

    data_dict = dict()
    data_dict["train"] = df_ants.take(range(round(n_train)), axis=0)
    data_dict["validation"] = df_ants.loc[set(df_ants.index) - set(data_dict["train"].index)].take(range(round(n_val)))
    data_dict["test"] = df_ants.loc[
        set(df_ants.index) - set(data_dict["train"].index) - set(data_dict["validation"].index)]

    # Serialize csv
    for df_name, df in data_dict.items():
        record_path = os.path.join(data_fldr, df_name, df_name + ".record")
        writer = tf.io.TFRecordWriter(record_path)
        for group in df.iterrows():
            img_path = os.path.join(images_source_fldr,
                                    __version__,
                                    df_ants.set_index("filename").loc[group[1].filename].source,
                                    group[1].filename)
            new_img_path = os.path.join(data_fldr, df_name, "images", group[1].filename)
            shutil.copyfile(img_path, new_img_path)
            tf_example = create_tf_example(group[1], img_path, label_map)
            writer.write(tf_example.SerializeToString())
        writer.close()


def to_pbtxt(label_map, label_map_path):
    lm_txt = list()
    for k, v in label_map.items():
        lm_txt.append('item {')
        lm_txt.append(' id: ' + str(v))
        lm_txt.append(' name: ' + '"' + k + '"')
        lm_txt.append('}')
        lm_txt.append('')
    with open(label_map_path, "w") as f:
        for line in lm_txt:
            f.write(line)
            f.write('\n')


if __name__ == "__main__":
    params = ParamLoader("1")
    ws = WorkSpace(params)
    ws.initialize()
    load_data_to_workspace(ws)

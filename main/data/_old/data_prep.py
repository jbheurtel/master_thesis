# Rename Files in a folder

import os
import shutil
from drafts.main.util.data_prep import rename_screenshot, build_labels_from_xml


class DataPrep:
    def __init__(self, data_path):
        self.data_path = data_path
        if not os.path.exists(data_path):
            os.makedirs(self.data_path)
            txt = "created new directory {}".format(data_path)
            print(txt)

        self._create_dirs()
        self.loaded = list()

    def _create_dirs(self):
        files = os.listdir(self.data_path)
        self.scr_negative = os.path.join(self.data_path, "negative")
        self.scr_positive = os.path.join(self.data_path, "positive")
        if "negative" not in files:
            os.makedirs(self.scr_negative)
            txt = "created new directory {}".format(self.scr_negative)
            print(txt)
        if "positive" not in files:
            os.makedirs(self.scr_positive)
            txt = "created new directory {}".format(self.scr_positive)
            print(txt)

    def load_negatives(self, source):
        # just copy, and add the path to a txt file.
        if source not in self.loaded:
            source_files = os.listdir(source)
            source_files = list(filter(lambda x: ".png" in x, source_files))

            for i in source_files:
                scr = os.path.join(source, i)
                dst = os.path.join(self.scr_negative, i)
                shutil.copyfile(scr, dst)

            files_for_txt = list(map(lambda x: os.path.join("negative", x), source_files))
            txt_file = os.path.join(self.scr_negative, 'bg.txt')
            with open(txt_file, 'a') as f:
                f.writelines('\n'.join(files_for_txt))
            self.loaded.append(source)
            txt = "loaded {}".format(source)
            print(txt)
        else:
            print("already loaded")

    def load_positives(self, source):

        if source not in self.loaded:
            xml_path = os.path.join(source, "annotations.xml")
            build_labels_from_xml(xml_path, self.scr_positive)
            source_files = os.listdir(source)
            source_files = list(filter(lambda x: ".png" in x, source_files))

            for i in source_files:
                scr = os.path.join(source, i)
                dst = os.path.join(self.scr_positive, i)
                shutil.copyfile(scr, dst)

            self.loaded.append(source)
            txt = "loaded {}".format(source)
            print(txt)
        else:
            print("already loaded")

    def rename_images_in_folder(self, folder):

        if folder == "positive":
            path = self.scr_positive
            txt_file = os.path.join(path, 'info.txt')
        elif folder == "negative":
            path = self.scr_negative
            txt_file = os.path.join(path, 'bg.txt')
        else:
            exit("folder must be either positive or negative")

        files = os.listdir(path)
        images = list(filter(lambda x: ".png" in x, files))
        old_new_names = dict()
        for i in images:
            new_i = rename_screenshot(i)
            old_new_names[i] = new_i
            os.rename(os.path.join(path, i), os.path.join(path, new_i))

        with open(txt_file) as f:
            lines = f.readlines()

        lines = "".join(lines)
        for key, val in old_new_names.items():
            lines = lines.replace(key, val)
        with open(txt_file, 'w') as f:
            f.writelines(lines)

        txt = "renamed images in folder: {}".format(folder)
        print(txt)


if __name__ == '__main__':
    ws = r"/Users/jbheurtel/Desktop/Own_Data/Test_WS"
    session = DataPrep(ws)

    source = r"/Users/jbheurtel/Desktop/Own_Data/Classified/Negative"
    session.load_negatives(source)

    source = r"/Users/jbheurtel/Desktop/Own_Data/Classified/Positive"
    session.load_positives(source)

    session.rename_images_in_folder("positive")
    session.rename_images_in_folder("negative")

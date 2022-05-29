import os
import shutil
import errno
from datetime import datetime


class File:
    def __init__(self, path):
        if os.path.exists(path):
            self.path = path
            self.base = os.path.basename(self.path)

            self.dir = os.path.dirname(self.path)

            dot_position = self.base.rfind(".")
            if dot_position == -1:
                self.file_name = None
                self.extension = None
                self.file_type = "directory"

            else:
                self.file_name = self.base[:dot_position]
                self.extension = self.base[dot_position:]
                self.file_type = "file"

            self.last_access_date = datetime.fromtimestamp(os.path.getatime(path)).strftime("%Y-%m-%d-%H-%M-%S")
            self.last_modification_date = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d-%H-%M-%S")
            self.creation_date = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d-%H-%M-%S")

        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    def rename(self, new_name):
        new_path = os.path.join(self.dir, new_name + self.extension)
        count = 1
        while os.path.exists(new_path):
            new_path = os.path.join(self.dir, new_name + "_" + str(count) + self.extension)
            count = count + 1
        try:
            os.rename(self.path, new_path)
            new_file = File(new_path)
            self.path = new_file.path
            self.file_name = new_file.file_name
        except:
            print("bad file name " + self.file_name)

    def move(self, new_dir):
        new_path = os.path.join(new_dir, self.file_name + self.extension)
        count = 1
        while os.path.exists(new_path):
            new_path = os.path.join(new_dir, self.file_name + "_" + str(count) + self.extension)
            count = count + 1
        shutil.move(self.path, new_path)
        self.path = new_path

    def copy(self, to_dir):
        new_path = os.path.join(to_dir, self.file_name + self.extension)
        count = 1
        while os.path.exists(new_path):
            new_path = os.path.join(to_dir, self.file_name + "_" + str(count) + self.extension)
            count = count + 1

        shutil.copyfile(self.path, new_path)

    def delete(self):
        os.remove(self.path)


if __name__ == '__main__':
    path = r"/Volumes/JEAN-BAPTIS/Photos/proxies/derivatives/00/00/1c/testing_stuff.jpg"
    file = File(path)
    file.rename("testing_stuff2")
    file.copy(r"/Users/jean-baptisteheurtel/Desktop")
    file.move(r"/Volumes/JEAN-BAPTIS/Photos")
    file.move(r"/Volumes/JEAN-BAPTIS/Photos/proxies/derivatives/00/00/1c")
    file.rename(r"testing_stuff")

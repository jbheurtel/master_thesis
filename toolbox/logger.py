import os
from datetime import datetime


class TxTLogger:
    def __init__(self, path, new=False, name="logger"):
        self.delimiter = " --- "
        self.path = os.path.join(path, name + ".txt")
        if not os.path.exists(self.path) or new:
            msg = "created" + self.delimiter + str(datetime.now()) + "\n"
            init_done = "done" + self.delimiter + "initialization" + "\n"
            file = open(self.path, "w")
            file.write(msg)
            file.write(init_done)
            file.close()

    def update(self, msg_key, msg_value):
        file = open(self.path, 'a')
        timestamp = "opened" + self.delimiter + str(datetime.now()) + "\n"
        msg = msg_key + self.delimiter + msg_value + "\n"
        file.write(timestamp)
        file.write(msg)
        file.close()

    def to_dict(self):
        with open(self.path, 'r') as file:
            content = file.read()
        lines = content.split("\n")
        lines = [line for line in lines if line != ""]
        lines = [line for line in lines if "opened" not in line]
        res = dict()
        for i in lines:
            msg_key, msg_value = i.split(self.delimiter)
            if msg_key not in res.keys():
                res[msg_key] = [msg_value]
            else:
                res[msg_key].append(msg_value)
        return res


if __name__ == "__main__":
    path = r'/Users/jean-baptisteheurtel/Main/work/SGCIB'
    log = TxTLogger(path, new=True)
    log.update("hello", "test")
    log.update("done", "task 1")
    log.update("done", "task 2")
    print(log.to_dict())

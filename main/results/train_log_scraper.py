import os
from toolbox.config import get_config

# INPUTS
model = "mgrain"
d_type = "train"

res_folder = get_config().results
log_path = os.path.join(res_folder, model, "train_log.rtf")

with open(log_path, 'r') as file:
    text = file.read()

lines = text.split("Epoch")
import pandas as pd
training_summary = pd.DataFrame(columns=["epoch", "time", "det_loss", "cls_loss", "box_loss",
                                         "reg_l2_loss", "loss", "learning_rate", "gradient_norm"])

for line in lines:

    if "=============" in line:
        new_df_line= pd.Series(name=int(line.split("\\\n85/85")[0].split("/")[0]), dtype=float)
        new_df_line["epoch"] = int(line.split("\\\n85/85")[0].split("/")[0])
        new_df_line["total_epochs"] = int(line.split("\\\n85/85")[0].split("/")[1])
        new_df_line["time"] = int(line.split("s")[0].rsplit(" ")[-1])
        new_df_line["det_loss"] = float(line.split("det_loss: ")[1].split(" - ")[0])
        new_df_line["cls_loss"] = float(line.split("cls_loss: ")[1].split(" - ")[0])
        new_df_line["box_loss"] = float(line.split("box_loss: ")[1].split(" - ")[0])
        new_df_line["reg_l2_loss"] = float(line.split("reg_l2_loss: ")[1].split(" - ")[0])
        new_df_line["loss"] = float(line.split("loss: ")[1].split(" - ")[0])
        new_df_line["learning_rate"] = float(line.split("learning_rate: ")[1].split(" - ")[0])
        new_df_line["gradient_norm"] = float(line.split("gradient_norm: ")[1].split("\\\n")[0])
        training_summary=  training_summary.append(new_df_line)


training_summary.to_csv(os.path.join(log_path.replace(".rtf", ".csv")))

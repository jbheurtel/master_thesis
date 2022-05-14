original = r"/Users/jbheurtel/Desktop/MT2/main/model/ssd_inception_v2_coco/pipeline.config.txt"
copy = r"/Users/jbheurtel/Desktop/MT2/main/model/ssd_inception_v2_coco/pipeline_copy.config.txt"
copy2 = r"/Users/jbheurtel/Desktop/MT2/main/model/ssd_inception_v2_coco/pipeline_copy_filled.config.txt"

import shutil
shutil.copyfile(original, copy)

with open(copy) as f:
    lines = f.readlines()

configs = {
    "INPUT_height": "3000",
    "INPUT_width": "3000"
}

for k, v in configs.items():
    lines = [x.replace(k,v) for x in lines]


with open(copy2, "w") as outfile:
    outfile.write("".join(lines))

# remove the fucking .txt
import shutil
shutil.copyfile(copy2, copy2.replace(".txt", ""))



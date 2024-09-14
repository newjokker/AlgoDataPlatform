
import os
import shutil
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.JsonUtil import JsonUtil


label_dir       = r"/home/ldq/Data/labels"
label_image_dir       = r"/home/ldq/Data/labels/images"
customer_dir    = r"/home/ldq/Data/customer_file"

for each in FileOperationUtil.re_all_file(label_dir, endswitch=[".json"]):
    json_info = JsonUtil.load_data_from_json_file(each)
    
    for obj in json_info["pic_describe"]:
        print(obj[1])
        obj[1] = obj[1].replace("192.168.3.50", "ENV_HOST")
        # obj[1] = obj[1].replace("", "ENV_HOST")


        file_name = os.path.split(obj[1])[1]

        customer_file_path = os.path.join(customer_dir, file_name)
        image_file_path = os.path.join(label_image_dir, file_name)

        if not os.path.exists(image_file_path):
            shutil.copy(customer_file_path, image_file_path)

    # JsonUtil.save_data_to_json_file(json_info, each)





from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.JsonUtil import JsonUtil


label_dir = r"/home/ldq/Data/labels"

for each in FileOperationUtil.re_all_file(label_dir, endswitch=[".json"]):
    json_info = JsonUtil.load_data_from_json_file(each)
    
    for obj in json_info["pic_describe"]:
        print(obj[1])
        obj[1] = obj[1].replace("192.168.3.50", "ENV_HOST")

    JsonUtil.save_data_to_json_file(json_info, each)


# copy to label image dir




import os
import time
import json
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from config import UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, r, REDIS_JSON_INFO
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel

ucd_router = APIRouter(prefix="/ucd", tags=["ucd"])


def get_json_file_info(ucd_name, is_official=True):

    ucd_name = str(ucd_name).strip('"')
    
    if not ucd_name.endswith(".json"):
        ucd_name += ".json"

    if is_official:
        file_path = os.path.join(UCD_OFFICIAL_DIR, ucd_name)
    else:
        file_path = os.path.join(UCD_CUSTOMER_DIR, ucd_name)

    if not os.path.exists(file_path):
        return HTTPException(status_code=500, detail=f"can't find json path : {file_path}")

    info = get_json_file_info_from_redis(file_path)
    if info:
        return info
    else:
        return get_json_file_info_from_file(file_path)

def get_json_file_info_from_file(file_path):
    file_info = None
    if os.path.exists(file_path):

        with open(file_path, 'r', encoding="utf-8") as json_file:
            json_info = json.load(json_file)

        count_tags_info = {}
        if "shapes" in json_info:
            for each_uc in json_info["shapes"]:
                for each_obj in json_info["shapes"][each_uc]:
                    each_label = each_obj["label"]
                    if each_label in count_tags_info:
                        count_tags_info[each_label] += 1
                    else:
                        count_tags_info[each_label] = 1
            
        file_info = {
            "add_time": "",
            "dataset_name": "",
            "describe": "",
            "json_path": "",
            "label_used": "",
            "model_name": "",
            "model_version": "",
            "update_time": "",
        }

        for each in file_info:
            if each in json_info:
                value = json_info[each]
                file_info[each] = str(value)
            else:
                file_info[each] = "null"

        file_info["count_tags_info"] = count_tags_info

        if file_info["json_path"]:
            file_info["json_name"] = os.path.split(file_path)[1]
        else:
            file_info["json_name"] = ""

        if file_info["update_time"] and file_info["update_time"] != "-1.0":
            file_info["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(file_info["update_time"])))

        if file_info["add_time"] and file_info["add_time"] != "-1.0":
            file_info["add_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(file_info["add_time"])))

        if "uc_list" in json_info:
            file_info["uc_count"] = str(len(json_info["uc_list"]))
        else:
            file_info["uc_count"] = "0"

        file_info["size"] = f"{os.path.getsize(file_path)/(1024*1024):.2f} M"

    save_json_info_to_redis(file_info, file_path)
    return file_info

def save_json_info_to_redis(json_info, file_path):
    json_info_str = json.dumps(json_info)
    r.hset(REDIS_JSON_INFO, file_path, json_info_str)

def get_json_file_info_from_redis(file_path):
    info = r.hget(REDIS_JSON_INFO, file_path)
    if info is not None:
        json_info = json.loads(info.decode("utf-8"))
        return json_info
    else:
        return info

def delete_info_from_redis(ucd_path):
    r.hdel(REDIS_JSON_INFO, ucd_path)

@ucd_router.get("/official/{ucd_name:path}")
async def get_ucd_official_file(ucd_name:str):
    """下载 ucd, 返回的是文件无法在浏览器中直接查看"""
    
    if not ucd_name.endswith(".json"):
        ucd_name = ucd_name + ".json"

    ucd_official_path = os.path.join(UCD_OFFICIAL_DIR, ucd_name)

    print(ucd_official_path)

    if os.path.exists(ucd_official_path):
        return FileResponse(ucd_official_path, media_type = "application/json", filename=ucd_name)
    else:
        return HTTPException(status_code=500, detail=f"ucd_name : {ucd_name} not in official")

@ucd_router.get("/customer/{ucd_name:path}")
async def get_ucd_customer_file(ucd_name:str):
    """下载 ucd, 返回的是文件无法在浏览器中直接查看"""
    
    if not ucd_name.endswith(".json"):
        ucd_name = ucd_name + ".json"

    ucd_customer_path = os.path.join(UCD_CUSTOMER_DIR, ucd_name)

    if os.path.exists(ucd_customer_path):
        return FileResponse(ucd_customer_path, media_type = "application/json", filename=ucd_name)
    else:
        return HTTPException(status_code=500, detail=f"ucd_name : {ucd_name} not in customer")

@ucd_router.get("/check")
async def check_ucdataset():
    """打印所有的 ucdataset, 官方的或者非官方的"""
    ucd_dict = {"official":[], "customer":[]}

    # official
    for each_ucd in FileOperationUtil.re_all_file(UCD_OFFICIAL_DIR, endswitch=['.json']):
        each_ucd_name = each_ucd[len(UCD_OFFICIAL_DIR)+1:][:-5]
        ucd_dict["official"].append(each_ucd_name)

    # customer
    for each_ucd in FileOperationUtil.re_all_file(UCD_CUSTOMER_DIR, endswitch=['.json']):
        each_ucd_name = each_ucd[len(UCD_CUSTOMER_DIR)+1:][:-5]
        ucd_dict["customer"].append(each_ucd_name)
    return ucd_dict

@ucd_router.get("/delete/{ucd_name:path}")
def delete_ucdataset(ucd_name:str):

    if not ucd_name.endswith(".json"):
        ucd_name += ".json"

    ucd_path = os.path.join(UCD_CUSTOMER_DIR, ucd_name)

    if os.path.exists(ucd_path):
        os.remove(ucd_path)
        return {"status": f"* delete dataset success : {ucd_path}"}
    else:
        return HTTPException(status_code=500, detail=f"{ucd_path} not exists in customer_dir")

@ucd_router.post("/upload/{ucd_name:path}")
async def upload_ucdataset(ucd_name:str, file: UploadFile = File(...)):

    if ucd_name.endswith(".json"):
        ucd_name = ucd_name[:-5]

    save_ucd_path = os.path.join(UCD_CUSTOMER_DIR, ucd_name + '.json')
    contents = await file.read()

    if os.path.exists(save_ucd_path):
        return HTTPException(status_code=500, detail=f"{ucd_name} exists, change a new name")
    else:
        save_ucd_folder = os.path.split(save_ucd_path)[0]
        os.makedirs(save_ucd_folder, exist_ok=True)

        with open(save_ucd_path, "wb") as f:
            f.write(contents)

        delete_info_from_redis(ucd_path=save_ucd_path)
        return {"status": "success", "message": "upload file success"}

@ucd_router.get("/get_json_info/official/{ucd_name:path}")
async def get_json_info_official(ucd_name:str):
    return get_json_file_info(ucd_name, is_official=True)

@ucd_router.get("/get_json_info/customer/{ucd_name:path}")
async def get_json_info_official(ucd_name:str):
    return get_json_file_info(ucd_name, is_official=False)

@ucd_router.get("/get_all_json_info_from_redis")
async def get_all_json_info_from_redis():

    return_dict = {}
    info = r.hgetall(REDIS_JSON_INFO)

    for each in info.keys():
        return_dict[each.decode("utf-8")] = info[each].decode("utf-8")

    return return_dict







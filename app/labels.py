from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import markdown2
import os
import requests
import json
from JoTools.utils.LogUtil import LogUtil
from config import MYSQL_USER, LOG_DIR, APP_LOG_NAME, LABEL_DIR
from typing import List
from pydantic import BaseModel
from .tools import Label
from JoTools.utils.FileOperationUtil import FileOperationUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "labels", print_to_console=False)

label_router = APIRouter(prefix="/label", tags=["label"])


# TODO 先直接托管 .md 文件，使用网页的方式展示出来

# TODO: 还不如直接维护在 pingcode 上面，就是如何读取 pingcode 上面的信息，或者直接维护在 33 服务器上，直接使用 .md 的形式每次可以提交完善之后再去

# TODO: 中文名，英文名，描述，注意点【列表】，描述图片list，所属模型（只需要提一下最初的那个模型就行了），这个名字是部分大小写的


os.makedirs(LABEL_DIR, exist_ok=True)


class LabelInfo(BaseModel):
    json_str:str
    new_label:bool=False


@label_router.get("/get_labels")
async def get_labels():    
    return_info = {"labels": []}
    for each_file in os.listdir(LABEL_DIR):
        if each_file.endswith(".json"):
            return_info["labels"].append(each_file[:-5])
    return_info["status"] = "success"
    return return_info

@label_router.get("/get_label_info/{label_name}")
async def get_label_info(label_name:str):
    label_path = os.path.join(LABEL_DIR, f"{label_name}.json")
    a = Label(label_path)
    return  a.save_to_json_dict()

@label_router.post("/save_label_info")
async def update_label(label_info:LabelInfo):
    # json_str 转为 label， 保存到本地文件

    json_str = label_info.json_str
    new_label = label_info.new_label
    json_dict = json.loads(json_str)

    if json_dict["english_name"] in ["None", None]:
        log.error(f"update label failed, english_name is None")
        return {"status": "failed", "error_info": f"update label failed, english_name is None"}
    
    if json_dict["chinese_name"] in ["None", None]:
        log.error(f"update label failed, chinese_name is None")
        return {"status": "failed", "error_info": f"update label failed, chinese_name is None"}
   
    a = Label()
    a.load_from_json_dict(json_dict)
    json_file_path = os.path.join(LABEL_DIR, f"{a.english_name}.json")
    
    if os.path.exists(json_file_path):
        if not new_label:
            log.error(f"update label failed, new_label is False & label exists : {a.english_name}")
            return {"status": "failed", "error_info": f"update label failed, new_label is False & label exists : {a.english_name}"}
    else:
        a.update_create_time()

    a.save_to_json_file(json_file_path, update_time=True)
    log.info(f"* update label success : {a.english_name}")
    return {"status": "success"}    

@label_router.get("/show_label_info/{label_name}")
async def show_label_info(label_name:str):
    # 将 lable 转为读取为 html 的方式进行返回

    label_path = os.path.join(LABEL_DIR, f"{label_name}.json")

    if not os.path.exists(label_path):
        return {"error_info": f"json path not exists : {label_path}"}
    else:
        a = Label(label_path)
        log.info(a.save_to_json_dict())
        html = a.save_to_html_str()
        return HTMLResponse(content=html, status_code=200)




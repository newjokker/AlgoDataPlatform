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

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "labels", print_to_console=False)

label_router = APIRouter(prefix="/label", tags=["label"])


# TODO 先直接托管 .md 文件，使用网页的方式展示出来

# TODO: 还不如直接维护在 pingcode 上面，就是如何读取 pingcode 上面的信息，或者直接维护在 33 服务器上，直接使用 .md 的形式每次可以提交完善之后再去

# TODO: 中文名，英文名，描述，注意点【列表】，描述图片list，所属模型（只需要提一下最初的那个模型就行了），这个名字是部分大小写的


os.makedirs(LABEL_DIR, exist_ok=True)


class LabelInfo(BaseModel):
    json_str:str


@label_router.get("/get_label_info/{label_name}")
async def get_label(label_name:str):
    # 根据 labelname 从本地文件读取对应的文件返回对应的 json_str
    # 将 label 转为 html 格式的网页进行返回
    pass

@label_router.post("/save_label_info")
async def update_label(label_info:LabelInfo):
    # json_str 转为 label， 保存到本地文件
    json_str = label_info.json_str
    a = Label()
    json_dict = json.loads(json_str)
    a.load_from_json_dict(json_dict)

    json_file_path = os.path.join(LABEL_DIR, f"{a.english_name}.jpg")
    a.save_to_json_file(json_file_path)

@label_router.get("/show_label_info/{label_name}")
async def show_label_info(label_name:str):
    # 将 lable 转为读取为 html 的方式进行返回

    label_path = os.path.join(LABEL_DIR, f"{label_name}.json")
    a = Label()
    a.load_from_json_file(label_path)
    html = a.save_to_html_str()
    # html = markdown2.markdown(markdown_text)
    return HTMLResponse(content=html, status_code=200)




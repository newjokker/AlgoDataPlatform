from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import markdown2
import os
import requests
from JoTools.utils.LogUtil import LogUtil
from config import MYSQL_USER, LOG_DIR, APP_LOG_NAME, SERVER_HOST, SERVER_LOCAL_HOST, SERVER_PORT
from typing import List
from pydantic import BaseModel

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "labels", print_to_console=False)

label_router = APIRouter(prefix="/label", tags=["label"])


class Label(object):

    def __init__(self, english_name):
        self.chinese_name   = None              # 中文名也进行重复的区分
        self.english_name   = None              # 英文名不区分大小写
        self.set_english_name(english_name)     # 使用英文名唯一地去表示一个标签
        self.describe       = None
        self.attention      = set()
        self.pic_describe   = []                # （图片的说明，图片的地址直接计算上传的图片的 md5 即可）

    def add_pic_describe(describe, image_path):
        # 将图片使用 md5 的方式存储在本地
        pass

    def set_chinese_name(self, name):
        if " " in name:
            return False
        elif "," in name:
            return False
        elif "，" in name:
            return False
        elif name == "":
            return False
        else:
            self.chinese_name = name

    def set_english_name(self, name):
        if " " in name:
            return False
        elif "," in name:
            return False
        elif "，" in name:
            return False
        elif name == "":
            return False
        else:
            self.english_name = name

    def set_describe(self, des):
        self.des = des

    def add_attention(self, info):
        self.attention.add(info)

    def remove_attention(self, info):
        self.attention.add(info)

    def load_from_markdown(self, file_path):
        pass

    def load_from_json(self, json_str):
        # 从 json 中生成一个 Label
        pass

    def save_to_markdown(self, save_path):
        # 保存的时候有两种模式，一个是使用图片的路径，一个是直接使用图片的相对位置，图片保存下载放到一个文件夹里面去
        pass

    def save_to_html(self):
        html = markdown2.markdown("markdown_text")
        log.info(html)
        return HTMLResponse(content=html, status_code=200)

    def save_to_json(self):
        # 保存为 json 格式，用于方便在 http 上进行存储
        pass

    def _save_img_file(img_path):
        # 将图片数据存储到 custer_file 里面可以通过统一的路径进行管理

        if not os.path.exists(img_path):
            log.error(f"* file not exists : {img_path}")
            raise f"* file not exists : {img_path}"

        url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/customer_file/upload"
        with open(img_path, "rb") as file:
            files = {"file": (os.path.basename(img_path), file)}
            response = requests.post(url=url, files=files)
            file_path = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/customer_file/download/{response.text}"
            return file_path


# TODO 先直接托管 .md 文件，使用网页的方式展示出来

# TODO: 还不如直接维护在 pingcode 上面，就是如何读取 pingcode 上面的信息，或者直接维护在 33 服务器上，直接使用 .md 的形式每次可以提交完善之后再去

# TODO: 中文名，英文名，描述，注意点【列表】，描述图片list，所属模型（只需要提一下最初的那个模型就行了），这个名字是部分大小写的


class LabelInfo(BaseModel):
    json_str:str


@label_router.get("/get_label_info/{label_name}")
async def get_label(label_name:str):
    # 根据 labelname 从本地文件读取对应的文件返回对应的 json_str
    # 将 label 转为 html 格式的网页进行返回
    pass

@label_router.get("/save_label_info")
async def update_label(label_info:LabelInfo):
    # json_str 转为 label， 保存到本地文件
    pass

@label_router.get("/show_label_info/label_name")
async def show_label_info(label_name:str):
    # 将 lable 转为读取为 html 的方式进行返回
    pass




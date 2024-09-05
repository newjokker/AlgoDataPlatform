
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import markdown2
import os
import json
import requests
import time
from JoTools.utils.LogUtil import LogUtil
# from config import MYSQL_USER, LOG_DIR, APP_LOG_NAME, SERVER_HOST, SERVER_LOCAL_HOST, SERVER_PORT

from JoTools.utils.JsonUtil import JsonUtil
from JoTools.utils.TimeUtil import TimeUtil


SERVER_LOCAL_HOST = "192.168.3.50"
SERVER_PORT = 11106


# TODO: 将统计信息这一块进行完善



class Label(object):

    @staticmethod
    def get_time_str(mk_time=None):
        if mk_time is None:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mk_time))

    @staticmethod
    def get_struct_time(time_str, str_format):
        return time.strptime(time_str, str_format)

    @staticmethod
    def get_mk_time(time_str, str_format):
        return time.mktime(time.strptime(time_str, str_format))

    def __init__(self, json_file_path=""):
        self.chinese_name   = None              # 中文名也进行重复的区分
        self.english_name   = None              # 英文名不区分大小写
        self.describe       = None
        self.attention      = set()
        self.pic_describe   = []                # （图片的说明，图片的地址直接计算上传的图片的 md5 即可）
        self.create_time    = None
        self.update_time     = None
        self.stastic_info   = {}                # 存放统计信息，这个可以放在 redis 里面，需要打印的时候进行获取
        self.load_from_json_file(json_file_path)

    def add_pic_describe(self, describe, image_path, image_info={"width": 500}):
        # 将图片使用 md5 的方式存储在本地
        img_url = self._save_img_file(image_path)
        self.pic_describe.append((describe, img_url, image_info))

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
        self.describe = des

    def add_attention(self, info):
        self.attention.add(info)

    def remove_attention(self, info):
        self.attention.add(info)

    def load_from_json_dict(self, json_dict):
        # 从 json 中生成一个 Label

        self.set_chinese_name(json_dict["chinese_name"])
        self.set_english_name(json_dict["english_name"])
        self.set_describe(json_dict["describe"])

        self.create_time = json_dict.get("create_time", None)
        self.update_time = json_dict.get("update_time", None)

        self.attention = set()
        for each_attention in json_dict["attention"]:
            self.attention.add(each_attention)
        self.pic_describe = []
        for each_pic in json_dict["pic_describe"]:
            self.pic_describe.append(each_pic)

    def load_from_json_file(self, file_path):

        if not os.path.exists(file_path):
            return 

        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                json_dict = json.load(json_file)
                self.load_from_json_dict(json_dict=json_dict)
        except Exception as e:
            print(e)

    def save_to_html_str(self):
        # 保存的时候有两种模式，一个是使用图片的路径，一个是直接使用图片的相对位置，图片保存下载放到一个文件夹里面去

        # 使用 with 语句自动管理文件的打开和关闭
        with open(r"./app/templates/tag.html", "r", encoding="utf-8") as file:
            temp = file.read()

            # 标题
            temp = temp.replace("ENGLISH_NAME", str(self.english_name))
            temp = temp.replace("CHINESE_NAME", str(self.chinese_name))
            temp = temp.replace("DESCRIBE_STR", str(self.describe))
            temp = temp.replace("CREATE_TIME_STR", str(self.create_time))
            temp = temp.replace("UPDATE_TIME_STR", str(self.update_time))

            # 
            attention_str = ""
            for each_attention in self.attention:
                attention_str += f"<ul><li>{each_attention}</li></ul>\n"
            temp = temp.replace("ATTENTION_STR", attention_str)

            # 
            pic_str = ""
            for each_des, each_url, each_img_info in self.pic_describe:
                width = 500
                # 
                if "width" in each_img_info:
                    width = each_img_info["width"]
                pic_str += f"""<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{each_des}</p><p><img src="{each_url}" alt="" class="mw_img_center" style="width:{width}px;display: block; clear:both; margin: 0 auto;"/>\n"""
            temp = temp.replace("PIC_DES_STR", pic_str)

        return temp

    def save_to_html(self):
        html = markdown2.markdown("markdown_text")
        return HTMLResponse(content=html, status_code=200)

    def save_to_json_dict(self):
        # 保存为 json 格式，用于方便在 http 上进行存储
        
        json_info = {
            "english_name"  : self.english_name,
            "chinese_name"  : self.chinese_name,
            "describe"      : self.describe,
            "attention"     : list(self.attention),
            "pic_describe"  : self.pic_describe,
            "create_time"   : self.create_time,
            "update_time"   : self.update_time,
        }
        return json_info

    def update_create_time(self):
        self.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def update_update_time(self):
        self.update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def save_to_json_file(self, save_path):

        if self.create_time in [None, "None"]:
            self.update_create_time()

        if self.update_time in [None, "None"]:
            self.update_update_time()

        json_info = self.save_to_json_dict()
        try:
            with open(save_path, 'w', encoding="utf-8") as json_file:
                json.dump(json_info, json_file, indent=4)
        except Exception as e:
            print(e)

    def print_info(self):
        print(f"english name    : {self.english_name}")
        print(f"chinese name    : {self.chinese_name}")
        print(f"create time     : {self.create_time}")
        print(f"update time     : {self.update_time}")
        print(f"describe        : {self.describe}")
        print(f"attention       : ")
        for each_attention in self.attention:
            print(f"                * {each_attention}")
        print(f"pic_describe    : ")
        for each_pic in self.pic_describe:
            # print(f"                * {each_pic[1]} : {each_pic[0]}, {each_pic[3]}")
            print(f"                * {each_pic}")

    @staticmethod
    def _save_img_file(img_path):
        # 将图片数据存储到 custer_file 里面可以通过统一的路径进行管理

        if not os.path.exists(img_path):
            raise f"* file not exists : {img_path}"

        url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/customer_file/upload"
        with open(img_path, "rb") as file:
            files = {"file": (os.path.basename(img_path), file)}
            response = requests.post(url=url, files=files)
            file_name = json.loads(response.text)
            file_path = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/customer_file/download/{file_name}"
            return file_path


if __name__ == "__main__":

    json_file_path = "/usr/data/labels/test_md.json"

    a = Label(json_file_path)
    # a.chinese_name = "测试的标签"
    # a.describe = "这就是一个测试的标签，看看测试功能是不是有用"
    # a.add_attention("写的测试标签需要和当前的标注文档相兼容")
    # a.add_attention("要能将标签的信息生成一个标准话的文档，这样方便查看和处理")
    # a.add_pic_describe("这是一个图片的描述", image_path=r"/home/ldq/del/res/Egk001r.jpg")
    # a.print_info()
    # a.save_to_json_file("/home/ldq/del/test_md.json")

    a.print_info()

    # print(a.save_to_html_str())

    a.save_to_json_file(json_file_path)



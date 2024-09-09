

import os
import time
import json
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from config import STASTIC_TAG_DIR, STASTIC_LABEL_DIR, r, REDIS_JSON_INFO
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from JoTools.utils.JsonUtil import JsonUtil
import shutil


os.makedirs(STASTIC_TAG_DIR, exist_ok=True)
os.makedirs(STASTIC_LABEL_DIR, exist_ok=True)


stastic_router = APIRouter(prefix="/stastic", tags=["stastic"])


@stastic_router.get("/stastic_tags/{date_str}")
async def show_stastic_tags(date_str:str):
    if date_str == "today":
        date_str = time.strftime("%Y-%m-%d", time.localtime())
    date_json = os.path.join(STASTIC_TAG_DIR, f"{date_str}.json")   

    if not os.path.exists(date_json):
        return {"status": "failed", "error_info": f"no stastic_tag json found : {date_json}"}

    tag_info = JsonUtil.load_data_from_json_file(date_json)

    with open(r"./app/templates/stastic_tag.html", "r", encoding="utf-8") as file:
        temp = file.read()

        # stastic info
        tag_stastic_info = ""
        for each_tag_name, each_tag_count in tag_info["tag_count_stastic"]:
            tag_stastic_info += f"""
            <tr>
            <td>{each_tag_name}</td>
            <td>{each_tag_count}</td>
            </tr>\n
            """
        
        # not in sql
        tag_not_in_mysql_str = ""
        for each_tag, file_path_list in tag_info["tags_not_in_mysql"]:
            tag_not_in_mysql_str += f"<h4 >{each_tag}</h4>"
            for each_file_path in file_path_list:
                tag_not_in_mysql_str += f"<li>{each_file_path}</li>"
        
        # in sql
        tag_in_mysql_str = ""
        for each_tag, file_path_list in tag_info["tags_in_mysql"]:
            tag_in_mysql_str += f"<h4 >{each_tag}</h4>"
            for each_file_path in file_path_list:
                tag_in_mysql_str += f"<li>{each_file_path}</li>"
        
        temp = temp.replace("UPDATE_TIME_STR", tag_info["update_time"])
        temp = temp.replace("STASTIC_TAG_COUNT_STR", tag_stastic_info)
        temp = temp.replace("TAG_NOT_IN_MYSQL_STR", tag_not_in_mysql_str)
        temp = temp.replace("TAG_IN_MYSQL_STR", tag_in_mysql_str)

        return HTMLResponse(content=temp, status_code=200)

@stastic_router.get("/stastic_labels/{date_str}")
async def show_stastic_labels(date_str:str):
    """对已跟踪的数据 Lable 进行统计"""

    # 一个 uc 中的 label 要进行去重处理
    # 在展示的时候一个模型有多个版本，之展示其中最新的一个版本，
    # 因为 label 的个数非常多，如何快速地进行统计，因为 label 是不会变的，
    # （1）将历史的数据存在 redis 里面方便查询 
    # （2）同一个 uc 中的同一个标签默认是标完的, 对于每一个 uc ，记录每一个标签的最大的个数，并记录最大个数的模型的名字和版本，这样只要对比个数就行
    # （3）可能存在历史数据集存在问题，会抛弃掉一部分数据，该如何处理这个问题

    if date_str == "today":
        date_str = time.strftime("%Y-%m-%d", time.localtime())
    date_json = os.path.join(STASTIC_LABEL_DIR, f"{date_str}.json")   

    if not os.path.exists(date_json):
        return {"status": "failed", "error_info": f"no stastic_label json found : {date_json}"}

    pass

@stastic_router.post("/upload_stastic_info")
async def upload_stastic_info(file:UploadFile=File(...), save_type: str=Form(), save_name:str=Form(), over_write:bool=Form()):
    """上传统计数据"""

    # response = requests.post(url, files={'file': (file_path, file)}, \
    # data={"save_type": "tag", "save_name": "2024-09-08.json", "over_write": False})

    if save_type == "tag":
        save_dir = STASTIC_TAG_DIR
    elif save_type == "label":
        save_dir = STASTIC_LABEL_DIR
    else:
        # raise HTTPException(status_code=400, detail="save_type need in ['tag', 'label']")
        return {"status": "failed", "error_info": f"save_type need in ['tag', 'label'] : {save_name}"} 

    if not save_name.endswith(".json"):
        # raise HTTPException(status_code=400, detail="save_name need a json")
        return {"status": "failed", "error_info": f"save_name need a json : {save_name}"} 

    save_path = os.path.join(save_dir, save_name)

    if os.path.exists(save_path) and (over_write is False):
        # raise HTTPException(status_code=400, detail="file exists and over_write is False")
        return {"status": "failed", "error_info": f"file exists and over_write is False"} 

    # save to assign path
    with open(save_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
        return {"status": "success"}



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(stastic_router, host="0.0.0.0", port=12345)







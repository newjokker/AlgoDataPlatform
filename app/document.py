

import os
import time
import json
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
# from config import UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, r, REDIS_JSON_INFO
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from JoTools.utils.TimeUtil import TimeUtil
from JoTools.utils.JsonUtil import JsonUtil

STASTIC_TAG_DIR = f"F:\data\stastic\stastic_tags"


# doc_router = APIRouter(prefix="/doc", tags=["doc"])


os.makedirs(STASTIC_TAG_DIR, exist_ok=True)

doc_router = FastAPI()

@doc_router.get("/stastic_tags/{date_str}")
def show_stastic_tags(date_str:str):
    if date_str == "today":
        date_str = time.strftime("%Y-%m-%d", time.localtime())
    date_json = os.path.join(STASTIC_TAG_DIR, f"{date_str}.json")   

    if not os.path.exists(date_json):
        return {"status": "failed", "error_info": f"no stastic_tag json found : {date_json}"}

    tag_info = JsonUtil.load_data_from_json_file(date_json)

    with open(r"F:\Code\algodataplatform\app\templates\stastic_tag.html", "r", encoding="utf-8") as file:
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
                tag_not_in_mysql_str += f"<li>{each_tag} -> {each_file_path}</li>"
        
        # in sql
        tag_in_mysql_str = ""
        for each_tag, file_path_list in tag_info["tags_in_mysql"]:
            tag_in_mysql_str += f"<h4 >{each_tag}</h4>"
            for each_file_path in file_path_list:
                tag_in_mysql_str += f"<li>{each_tag} -> {each_file_path}</li>"
        
        temp = temp.replace("UPDATE_TIME_STR", tag_info["update_time"])
        temp = temp.replace("STASTIC_TAG_COUNT_STR", tag_stastic_info)
        temp = temp.replace("TAG_NOT_IN_MYSQL_STR", tag_not_in_mysql_str)
        temp = temp.replace("TAG_IN_MYSQL_STR", tag_in_mysql_str)

        return HTMLResponse(content=temp, status_code=200)


# TODO: 每天的统计信息直接发送到这里进行页面展示

# TODO: 写一个自动将统计信息生成网页的一个功能

# TODO: 将标签展示也放到这个里面来，所有对外展示的 html 文档，全部是这个 document 需要管理的内容

# TODO: 对应的应该是一个标准的 json 格式的数据 + .html 展示页面 = doc 








# TODO: pingcode 的文档如何从外部读取， https://pingcode.tuxingkeji.com/open

# TODO: 将文档也整合进来

# TODO: 现在很多数据都存放在不同的地方找一个东西非常的难受，需要有一个统一的平台管理这些所有的数据



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(doc_router, host="0.0.0.0", port=12345)







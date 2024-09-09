

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
os.makedirs(STASTIC_TAG_DIR, exist_ok=True)

STASTIC_LABEL_DIR = f"F:\data\stastic\stastic_labels"
os.makedirs(STASTIC_LABEL_DIR, exist_ok=True)


stastic_router = APIRouter(prefix="/stastic", tags=["stastic"])

# stastic_router = FastAPI()

@stastic_router.get("/stastic_tags/{date_str}")
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

@stastic_router.get("/stastic_labels/{date_str}")
def show_stastic_labels(date_str:str):
    
    if date_str == "today":
        date_str = time.strftime("%Y-%m-%d", time.localtime())
    date_json = os.path.join(STASTIC_LABEL_DIR, f"{date_str}.json")   

    if not os.path.exists(date_json):
        return {"status": "failed", "error_info": f"no stastic_label json found : {date_json}"}

    pass



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(stastic_router, host="0.0.0.0", port=12345)







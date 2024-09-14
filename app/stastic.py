

import os
import time
import json
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from config import STASTIC_TAG_DIR, STASTIC_LABEL_DIR, r, REDIS_JSON_INFO, STASTIC_SVN_MODEL_DIR, ENV_HOST, SERVER_PORT
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from JoTools.utils.JsonUtil import JsonUtil
import shutil
from JoTools.utils.LogUtil import LogUtil
from config import LOG_DIR, APP_LOG_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "stastic", print_to_console=False)


os.makedirs(STASTIC_TAG_DIR, exist_ok=True)
os.makedirs(STASTIC_LABEL_DIR, exist_ok=True)
os.makedirs(STASTIC_SVN_MODEL_DIR, exist_ok=True)

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
        log.info(f"* stastic_tags : {date_str}")
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

    with open(r"./app/templates/stastic_label.html", "r", encoding="utf-8") as file:
        temp = file.read()
        json_info = JsonUtil.load_data_from_json_file(date_json)

        # label not in platform
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>label</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["label_not_in_platform"]:
            table_body += f"<tr><td>{each_line}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("LABEL_NOT_IN_PLATFORM", table_temp)

        # label in platform
        table_temp = ""
        for each_label in json_info["label_in_platform"]:
            table_temp += f'<li><a href="http://{ENV_HOST}:{SERVER_PORT}/label/show_label_info/{each_label}">{each_label}</a></li>'
        temp = temp.replace("LABEL_IN_PLATFORM", table_temp)

    temp = temp.replace("LABEL_LIST_INFO_URL", f'<a href="http://{ENV_HOST}:{SERVER_PORT}/label/show_label_list_info">已入库数据标签展示页面</a>')
    log.info(f"* stastic_labels : {date_str}")
    return HTMLResponse(content=temp, status_code=200)

@stastic_router.get("/stastic_svn_models/{date_str}")
async def show_stastic_svn_models(date_str:str):
    """对已跟踪的数据 Lable 进行统计"""

    if date_str == "today":
        date_str = time.strftime("%Y-%m-%d", time.localtime())
    date_json = os.path.join(STASTIC_SVN_MODEL_DIR, f"{date_str}.json")   

    if not os.path.exists(date_json):
        return {"status": "failed", "error_info": f"no stastic_label json found : {date_json}"}

    with open(r"./app/templates/stastic_svn_model.html", "r", encoding="utf-8") as file:
        temp = file.read()
        json_info = JsonUtil.load_data_from_json_file(date_json)

        # check model_path
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>file_path</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["path_error"]:
            table_body += f"<tr><td>{each_line}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("PATH_ERROR_TABLE", table_temp)

        # check version
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>file_path</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["version_error"]:
            table_body += f"<tr><td>{each_line}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("VERSION_ERROR_TABLE", table_temp)

        # check config
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>model_name</th>
    <th>model_version</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["no_config"]:
            table_body += f"<tr><td>{each_line[0]}</td><td>{each_line[1]}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("NO_CONFIG_ERROR_TABLE", table_temp)

        # check train_data
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>model_name</th>
    <th>model_version</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["no_train_data"]:
            table_body += f"<tr><td>{each_line[0]}</td><td>{each_line[1]}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("NO_TRAIN_DATA_ERROR_TABLE", table_temp)

        # check no non_encrypt_model
        table_temp = """
    <table>
    <thead>
    <tr>
    <th>model_name</th>
    <th>model_version</th>
    </tr>
    </thead>
    <tbody>

    TABLE_LINES

    </tbody>
    </table>
    """
        table_body = ""
        for each_line in json_info["no_non_encrypt_model"]:
            table_body += f"<tr><td>{each_line[0]}</td><td>{each_line[1]}</td></tr>"
        table_temp = table_temp.replace("TABLE_LINES", table_body)
        temp = temp.replace("NO_NON_ENTRYPT_MODEL_ERROR_TABLE", table_temp)
        log.info(f"* stastic_svn_models : {date_str}")
        return HTMLResponse(content=temp, status_code=200)

@stastic_router.post("/upload_stastic_info")
async def upload_stastic_info(file:UploadFile=File(...), save_type: str=Form(), save_name:str=Form(), over_write:bool=Form()):
    """上传统计数据"""

    # response = requests.post(url, files={'file': (file_path, file)}, \
    # data={"save_type": "tag", "save_name": "2024-09-08.json", "over_write": False})

    if save_type == "tag":
        save_dir = STASTIC_TAG_DIR
    elif save_type == "label":
        save_dir = STASTIC_LABEL_DIR
    elif save_type == "svn_model":
        save_dir = STASTIC_SVN_MODEL_DIR
    else:
        # raise HTTPException(status_code=400, detail="save_type need in ['tag', 'label']")
        log.error(f"* upload_stastic_info failed, save_type need in ['tag', 'label', 'svn_model'] : {save_name}")
        return {"status": "failed", "error_info": f"save_type need in ['tag', 'label', 'svn_model'] : {save_name}"} 

    if not save_name.endswith(".json"):
        # raise HTTPException(status_code=400, detail="save_name need a json")
        log.error(f"* upload_stastic_info failed, save_name need a json : {save_name}")
        return {"status": "failed", "error_info": f"save_name need a json : {save_name}"} 

    save_path = os.path.join(save_dir, save_name)

    if os.path.exists(save_path) and (over_write is False):
        # raise HTTPException(status_code=400, detail="file exists and over_write is False")
        log.error(f"* upload_stastic_info failed, file exists and over_write is False")
        return {"status": "failed", "error_info": f"file exists and over_write is False"} 

    # save to assign path
    with open(save_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
        log.info(f"* upload_stastic_info success")
        return {"status": "success"}



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(stastic_router, host="0.0.0.0", port=12345)







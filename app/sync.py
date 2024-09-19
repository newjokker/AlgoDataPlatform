
from fastapi import APIRouter
from config import MYSQL_USER, LOG_DIR, MYSQL_PASSWORD, MYSQL_HOST, \
        APP_LOG_NAME, MYSQL_DATABASE_NAME, MYSQL_TABLE_NAME, REMOTE_SYNC_DIR ,\
        DATA_DIR
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
import pymysql
from typing import List
from pydantic import BaseModel
import os
from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "sync", print_to_console=False)


sync_router = APIRouter(prefix="/sync", tags=["sync"])


os.makedirs(REMOTE_SYNC_DIR, exist_ok=True)


# 同步的命令
# TODO: rsync -avu --progress ldq@192.168.3.33:/home/raid5/data_ucd/root_dir/json_img/* /usr/data/img_cache/



# TODO: 这个同步是指在多个数据服务器平台之间进行同步，只要指定其他数据平台的 IP HOST, 就能直接使用其他数据平台的数据，同步到当前的数据平台上，这样就可以实现分布式部署，需要注意的是各个数据平台存在的版本可能不一样，需要有一个 md5 校验
# TODO: 其他数据平台的配置信息直接卸载 sync 文件夹中


@sync_router.get("/ucd_official")
def update_ucd_official():
    # TODO: 点击自动同步 ucd officical ，删除再下载，或者只下载没有的之类的功能
    pass

@sync_router.get("/ucd_customer")
def update_ucd_customer():
    # TODO: 点击自动同步 ucd customer ，删除再下载，或者只下载没有的之类的功能
    pass

@sync_router.get("/ucd_json_img_cache")
def update_ucd_img_json_cache():
    # TODO: 点击扫描追踪的服务器的指定地址今天的新增数据有没有同步过来，也可以同步历史数据
    pass

@sync_router.get("/file/{file_path:path}")
def update_files(file_path:str):
    # TODO: 传递相对位置，如果这个机器中有对应的文件的话，直接返回对应文件

    file_path = os.path.join(DATA_DIR, file_path)
    if os.path.exists(file_path):
        # return FileResponse(ucd_official_path, media_type = "application/octet-stream", filename=ucd_name)
        pass
    else:
        return HTTPException(status_code=500, detail=f"file not found")

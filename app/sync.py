
from fastapi import APIRouter
from config import MYSQL_USER, LOG_DIR, MYSQL_PASSWORD, MYSQL_HOST, APP_LOG_NAME, MYSQL_DATABASE_NAME, MYSQL_TABLE_NAME
from fastapi.exceptions import HTTPException
import pymysql
from typing import List
from pydantic import BaseModel
import os
import request

from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "sync", print_to_console=False)


sync_router = APIRouter(prefix="/sync", tags=["sync"])


@sync_router.get("/ucd_official")
def update_ucd_official():
    # TODO: 点击自动同步 ucd officical ，删除再下载，或者只下载没有的之类的功能
    pass

@sync_router.get("/ucd_customer")
def update_ucd_customer():
    # TODO: 点击自动同步 ucd customer ，删除再下载，或者只下载没有的之类的功能
    pass

@sync_router.get("/ucd_img_json_cache")
def update_ucd_img_json_cache():
# TODO: 点击扫描追踪的服务器的指定地址今天的新增数据有没有同步过来，也可以同步历史数据
    pass



# 同步的数据平台，可以将指定的同步数据直接发送到这边进行保存，可以配置同步的信息，保存的规则等等

# 同步的数据类型，
# 同步的
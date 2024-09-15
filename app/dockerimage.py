
import os
import time
import json
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from config import UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, r, REDIS_JSON_INFO, STASTIC_TAG_DIR, LOG_DIR, APP_LOG_NAME
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from JoTools.utils.TimeUtil import TimeUtil
from JoTools.utils.JsonUtil import JsonUtil
from JoTools.utils.LogUtil import LogUtil


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "dockerimage", print_to_console=False)


doc_router = APIRouter(prefix="/dockerimage", tags=["dockerimage"])




# 管理 svn 上面的 基础镜像，和获取各个服务器上的 docker 镜像的信息
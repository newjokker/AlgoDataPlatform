
import os
import time
import json
import subprocess
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from JoTools.utils.TimeUtil import TimeUtil
from JoTools.utils.JsonUtil import JsonUtil
from JoTools.utils.LogUtil import LogUtil
from config import UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, r, REDIS_JSON_INFO, STASTIC_TAG_DIR, LOG_DIR, APP_LOG_NAME, DOCKRIMAGE_DIR, IMAGE_SVN_ROOT

# DATA_DIR            = r"/home/ldq/Data"
# IMAGE_SVN_ROOT      = r"svn://192.168.3.101/repository/基础镜像"
# LOG_DIR             = os.path.join(DATA_DIR, "logs") 
# APP_LOG_NAME        = "app.log"
# SVN_ROOT            = r"svn://192.168.3.101/repository"
# SVN_USERNAME        = "txkj"
# SVN_PASSWORD        = "txkj"
# SVN_IGNORE_DIR      = {"基础镜像", "Other", "OTHER-专项"}
# DOCKRIMAGE_DIR      = os.path.join(DATA_DIR, "dockerimage")


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "dockerimage", print_to_console=False)

os.makedirs(DOCKRIMAGE_DIR, exist_ok=True)
dockerimage_router = APIRouter(prefix="/dockerimage", tags=["dockerimage"])


def get_all_base_image():
    # official
    official_model_list = []
    svn_download_command = f"svn list {IMAGE_SVN_ROOT} --username {SVN_USERNAME} --password {SVN_PASSWORD} -R"
    result = subprocess.run(svn_download_command, shell=True, check=True, text=True, capture_output=True).stdout
    
    result = result.split("\n")
    for each_model_path in result:
        if not each_model_path:
            continue

        official_model_list.append(each_model_path)

    return official_model_list

def get_all_base_image_loacl():
    # official
    image_path_list = []
    for i, j, each_image_path in os.walk(DOCKRIMAGE_DIR):
        image_path_list.append(each_image_path)
    return image_path_list

def sync_from_svn(image_path):
    save_path = os.path.join(DOCKRIMAGE_DIR, image_path)
    
    if not os.path.exists(save_path):
        svn_download_command = f"svn export {IMAGE_SVN_ROOT}/{image_path}  {save_path}  --username {SVN_USERNAME} --password {SVN_PASSWORD}"
        print(svn_download_command)
        result = subprocess.run(svn_download_command, shell=True, check=True, text=True, capture_output=True).stdout
        print(result)
    else:
        print(f"* file exists : {save_path}")

@dockerimage_router.get("/check")
def check():
    all_base_img = get_all_base_image()
    log.info("* dockerimage check")
    return {"status": "success", "image_list": all_base_img}

@dockerimage_router.get("/check_local")
def check_local():
    all_base_img = get_all_base_image_loacl()
    log.info("* dockerimage check")
    return {"status": "success", "image_list": all_base_img}

@dockerimage_router.get("/download_command/{file_path:path}")
async def get_download_command(file_path:str):
    svn_download_command = f"svn export {IMAGE_SVN_ROOT}/{file_path}  save_path  --username {SVN_USERNAME} --password {SVN_PASSWORD}"
    return svn_download_command


# 管理 svn 上面的 基础镜像，和获取各个服务器上的 docker 镜像的信息

# TODO: 将我平时用的基础镜像放在 svn 上面，我自己进行同步


if __name__ == "__main__":

    all_image = get_all_base_image()

    local_models = get_all_base_image_loacl()
    print(local_models)


    for each in all_image:
        print(each)

        sync_from_svn(each)

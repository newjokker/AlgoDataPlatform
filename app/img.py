import os
import random
import shutil
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from config import UC_IMG_DIR
from fastapi.exceptions import HTTPException
from JoTools.utils.LogUtil import LogUtil
from config import LOG_DIR, APP_LOG_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "uc", print_to_console=False)


img_router = APIRouter(prefix="/file", tags=["img"])


@img_router.get("/{uc_suffix}")
async def download_uc_file(uc_suffix:str):
    """下载 image,json"""
    file_path = os.path.join(UC_IMG_DIR, uc_suffix[:3], uc_suffix)

    if not os.path.exists(file_path):
        return {"error": f"* no such file path : {file_path}"}

    if uc_suffix.endswith(".jpg"):
        with open(file_path, 'rb') as f:
            image_file = f.read()
            return Response(image_file, media_type='image/jpeg')
    elif uc_suffix.endswith(".json"):
        with open(file_path, 'rb') as f:
            json_file = f.read()
        return Response(json_file, media_type='application/json')
    else:
        return {"error": "suffix error, suffix must in ['.jpg', '.json']"}


@img_router.post("/upload")
async def upload_img_file(file: UploadFile = File(...)):
    if ucd_name.endswith(".json"):
        ucd_name = ucd_name[:-5]

    save_ucd_path = os.path.join(UC_IMG_DIR, ucd_name + '.json')
    contents = await file.read()

    if os.path.exists(save_ucd_path):
        return HTTPException(status_code=500, detail=f"{ucd_name} exists, change a new name")
    else:
        save_ucd_folder = os.path.split(save_ucd_path)[0]
        os.makedirs(save_ucd_folder, exist_ok=True)

        with open(save_ucd_path, "wb") as f:
            f.write(contents)

        return {"status": "success", "message": "upload file success"}



# TODO: 和入库的文件夹分隔开，如果这下面没有对应的文件直接去指定文件夹拷贝一份过来

# TODO: 支持入库的服务，但是需要权限，将入库的代码写小一点，不然太麻烦了

# TODO: 旋转的代码无法入库，对数据进行处理，有数据无法出处理，直接返回错误即可





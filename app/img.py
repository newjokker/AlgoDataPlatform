import os
import random
import shutil
from fastapi import APIRouter
from fastapi.responses import FileResponse, Response
from config import UC_IMG_DIR


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



# TODO: 支持入库的服务，但是需要权限，将入库的代码写小一点，不然太麻烦了







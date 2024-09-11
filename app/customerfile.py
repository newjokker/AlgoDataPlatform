import os
import random
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from config import CUSTOMER_FILE_DIR, LOG_DIR, APP_LOG_NAME
from fastapi.exceptions import HTTPException
from JoTools.utils.LogUtil import LogUtil
from JoTools.utils.HashlibUtil import HashLibUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "customer_file", print_to_console=False)


os.makedirs(CUSTOMER_FILE_DIR, exist_ok=True)


customer_file_router = APIRouter(prefix="/customer_file", tags=["file"])


@customer_file_router.get("/download/{filename}")
async def download_file(filename:str):
    """下载所有存在的文件"""
    file_path = os.path.join(CUSTOMER_FILE_DIR, filename)
    if not os.path.exists(file_path):
        log.error(f"* no such file path : {file_path}")
        return {"error": f"* no such file path : {file_path}"}
    else:
        log.info(f"* file response : {file_path}")
        return FileResponse(file_path)

@customer_file_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传任意格式的文件"""
    contents = await file.read()
    suffix = os.path.splitext(file.filename)[1]
    save_path = os.path.join(CUSTOMER_FILE_DIR, str(uuid.uuid1()) + suffix)

    with open(save_path, "wb") as f:
        f.write(contents)

    file_md5 = HashLibUtil.get_file_md5(save_path)
    new_path = os.path.join(CUSTOMER_FILE_DIR, file_md5 + suffix)
    shutil.move(save_path, new_path)
    log.info(f"* upload success : {new_path}")
    return file_md5 + suffix


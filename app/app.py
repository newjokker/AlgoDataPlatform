import os
from fastapi import APIRouter
from JoTools.utils.FileOperationUtil import FileOperationUtil
from config import UCD_APP_DIR
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException



app_router = APIRouter(prefix="/app", tags=["app"])

async def get_version_list():
    version_list = []
    version_dict = {}

    for each_so_path in FileOperationUtil.re_all_file(UCD_APP_DIR):
        so_name = os.path.split(each_so_path)[1]
        version = so_name[4:]
        version_index_list = version[1:].split(".")
        version_index  = int(version_index_list[0]) * 1000000 + int(version_index_list[1]) * 1000 + int(version_index_list[2])
        version_dict[version_index] = version

    index_list = sorted(version_dict.keys())
    for each_index in index_list:
        version_list.append(version_dict[each_index])

    return version_list

@app_router.get("/ucd_version_list")
async def get_ucd_version_list():
    """返回所有的在线版本"""
    version_list = get_version_list()
    return {"ucd_version_info": version_list}

@app_router.get("/{ucd_version}")
async def get_ucd_app(ucd_version:str):
    ucd_app_path = os.path.join(UCD_APP_DIR, "ucd_" + ucd_version)

    if os.path.exists(ucd_app_path):
        return FileResponse(ucd_app_path)
    else:
        version_str = ",".join(get_version_list())
        return HTTPException(status_code=500, detail=f"version should in : [{version_str}]")
    

# TODO 支持上传 app 的接口，省得每次手动上传了




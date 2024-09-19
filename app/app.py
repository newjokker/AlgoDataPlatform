import os
from fastapi import APIRouter, UploadFile, File
from JoTools.utils.FileOperationUtil import FileOperationUtil
from config import UCD_APP_DIR
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from config import LOG_DIR, APP_LOG_NAME
from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "app", print_to_console=False)


os.makedirs(UCD_APP_DIR, exist_ok=True)


app_router = APIRouter(prefix="/app", tags=["app"])

def get_version_list():
    version_list = []
    version_dict = {}

    for each_so_path in FileOperationUtil.re_all_file(UCD_APP_DIR):
        so_name = os.path.split(each_so_path)[1]
        
        if not str(so_name).startswith("ucd_v"):
            continue

        version = so_name[4:]
        version_index_list = version[1:].split(".")
        version_index  = int(version_index_list[0]) * 1000000 + int(version_index_list[1]) * 1000 + int(version_index_list[2])
        version_dict[version_index] = version

    index_list = sorted(version_dict.keys())
    for each_index in index_list:
        version_list.append(version_dict[each_index])

    return version_list

def is_leagal_app_name(app_name):
    if not app_name.startswith("ucd_v"):
        return False
    
    app_v_list = app_name[5:].split(".")
    if len(app_v_list) != 3:
        return False
    
    for each_v in app_v_list:
        if not each_v.isdigit():
            return False
        
    return True

@app_router.get("/versions")
async def get_ucd_version_list():
    version_list = get_version_list()
    log.info("* get version list")
    return {"ucd_version_info": version_list}

@app_router.get("/load/{app_version}")
async def get_ucd_app(app_version:str):
    ucd_app_path = os.path.join(UCD_APP_DIR, "ucd_" + app_version)

    if os.path.exists(ucd_app_path):
        log.info(f"* load app : {app_version}")
        return FileResponse(ucd_app_path)
    else:
        version_str = ",".join(get_version_list())
        log.error(f"* load app failed, version should in : [{version_str}]")
        return HTTPException(status_code=500, detail=f"version should in : [{version_str}]")

@app_router.post("/upload/{app_name}")
async def upload_ucdataset(app_name:str, file: UploadFile = File(...)):

    if not is_leagal_app_name(app_name):
        log.error(f"* upload app failed : {app_name}, app_name : ucd_vx.y.z")
        return HTTPException(status_code=500, detail=f"app_name : ucd_vx.y.z")

    save_app_path = os.path.join(UCD_APP_DIR, app_name)
    if os.path.exists(save_app_path):
        log.error(f"* upload app failed, app_name exists : {app_name}")
        return HTTPException(status_code=500, detail=f"app_name exists : {app_name}")

    contents = await file.read()
    with open(save_app_path, "wb") as f:
        f.write(contents)

    log.info(f"* upload ucd app success : {app_name}")
    return {"status": "success", "message": "upload ucd app success"}






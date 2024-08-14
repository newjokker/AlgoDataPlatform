
import os
from fastapi import APIRouter
import subprocess
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from config import SVN_ROOT, SVN_PASSWORD, SVN_USERNAME, MODEL_SUFFIX_SET, TEMP_DIR, MODEL_CUSTOMER_DIR
from fastapi import APIRouter, File, UploadFile
from JoTools.utils.FileOperationUtil import FileOperationUtil


model_router = APIRouter(prefix="/model", tags=["model"])


def get_model_name_and_version_from_svn_url(model_url):
    model_path_split = model_url.split("/") 
    if len(model_path_split) < 5:
        return None, None
    else:
        a, b, c, name = model_path_split[:-4]
        if not (a.isdigit() and b.isdigit() and c.isdigit()):
            return None, None
        version = f"v{a}.{b}.{c}"
        return name, version 

@model_router.get("/check")
async def check_model():
    # official
    official_model_list = []
    svn_download_command = f"svn list {SVN_ROOT} --username {SVN_USERNAME} --password {SVN_PASSWORD} -R"
    result = subprocess.run(svn_download_command, shell=True, check=True, text=True, capture_output=True).stdout
    
    result = result.split("\n")
    for each_model_path in result:
        if not each_model_path:
            continue
        if os.path.splitext(each_model_path)[1] in MODEL_SUFFIX_SET:
            official_model_list.append(each_model_path)
    # customer
    customer_model_list = []
    for each_model_path in FileOperationUtil.re_all_file(MODEL_CUSTOMER_DIR, endswitch=list(MODEL_SUFFIX_SET)):
        each_model_path = each_model_path[len(MODEL_CUSTOMER_DIR):].lstrip("/")
        customer_model_list.append(each_model_path)
    return {"official": official_model_list, "customer": customer_model_list}

@model_router.get("/load/official/{model_path:path}")
async def load_model(model_path:str):

    model_suffix = os.path.splitext(model_path)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model_name suffix must in {MODEL_SUFFIX_SET}")
    
    model_dir, model_name   = os.path.split(model_path)
    save_model_dir          = os.path.join(TEMP_DIR, model_dir)
    model_save_path         = f"{save_model_dir}/{model_name}"

    if os.path.exists(model_save_path):
        return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
    else:
        os.makedirs(save_model_dir, exist_ok=True)
        svn_download_command = f"svn export {SVN_ROOT}/{model_path} {model_save_path} --username txkj --password txkj"
        try:
            subprocess.run(svn_download_command, shell=True, check=True)
            return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
        except subprocess.CalledProcessError as e:
            return HTTPException(status_code=500, detail=f"download from SVN failed : {model_path} , error : {e}")

@model_router.get("/load/customer/{model_path:path}")
async def load_model(model_path:str):

    model_suffix = os.path.splitext(model_path)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model_name suffix must in {MODEL_SUFFIX_SET}")
    
    model_dir, model_name   = os.path.split(model_path)
    save_model_dir          = os.path.join(MODEL_CUSTOMER_DIR, model_dir)
    model_save_path         = f"{save_model_dir}/{model_name}"

    if os.path.exists(model_save_path):
        return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
    else:
        return HTTPException(status_code=500, detail=f"model path not exists : {model_path}")
    
@model_router.get("/delete/{model_name:path}")
async def delete_model(model_name:str):

    model_suffix = os.path.splitext(model_name)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model suffix must in {MODEL_SUFFIX_SET}")

    model_path = os.path.join(MODEL_CUSTOMER_DIR, model_name)

    if os.path.exists(model_path):
        os.remove(model_path)
        return {"status": f"* delete dataset success : {model_path}"}
    else:
        return HTTPException(status_code=500, detail=f"{model_path} not exists in model customer dir")

@model_router.post("/upload/{model_name:path}")
async def upload_model(model_name:str, file: UploadFile = File(...)):

    model_suffix = os.path.splitext(model_name)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model suffix must in {MODEL_SUFFIX_SET}")

    save_model_path = os.path.join(MODEL_CUSTOMER_DIR, model_name)
    contents = await file.read()

    if os.path.exists(save_model_path):
        return HTTPException(status_code=500, detail=f"{model_name} exists, change a new name")
    else:
        save_model_folder = os.path.split(save_model_path)[0]
        os.makedirs(save_model_folder, exist_ok=True)

        with open(save_model_path, "wb") as f:
            f.write(contents)

        return {"status": "success", "message": "upload model success"}




# TODO: 找到模型的训练数据集和对应的 config.ini 文件

# TODO: load_model, 提供的是 svn 地址，或者模型的 md5

# TODO: 已经下载的模型在本地应该有缓存

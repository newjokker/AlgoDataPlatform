
import os
from fastapi import APIRouter
import subprocess
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from config import SVN_ROOT, SVN_PASSWORD, SVN_USERNAME, MODEL_SUFFIX_SET, TEMP_DIR, MODEL_CUSTOMER_DIR, MODEL_TRAIN_SUFFIX, MODEL_CONFIG_SIFFIX, SVN_IGNORE_DIR
from fastapi import APIRouter, File, UploadFile
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.LogUtil import LogUtil
from config import LOG_DIR, APP_LOG_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "model", print_to_console=False)

model_router = APIRouter(prefix="/model", tags=["model"])


os.makedirs(MODEL_CUSTOMER_DIR, exist_ok=True)


def get_model_name_and_version_from_svn_url(model_url):
    """模型名, 模型版本号, 模型文件的名子"""
    model_path_split = model_url.split("/") 
    if len(model_path_split) < 5:
        print("length < 5", model_path_split)
        return None, None, None
    else:
        model_name = "/".join(model_path_split[:-4])
        a, b, c, model_file_name = model_path_split[-4:]
        if not (a.isdigit() and b.isdigit() and c.isdigit()):
            print("not digit", model_url)
            return None, None, None
        version = f"v{a}.{b}.{c}"
        return model_name, version, model_file_name

def if_v1_gt_v2(v1_str, v2_str):
    v1 = v1_str[1:].split(".")
    v2 = v2_str[1:].split(".")

    v1 = [int(x) for x in v1]
    v2 = [int(x) for x in v2]

    if v1[0] > v2[0]:
        return True
    elif v1[0] < v2[0]:
        return False
    else:
        if v1[1] > v2[1]:
            return True
        elif v1[1] < v2[1]:
            return False
        else:
            if v1[2] > v2[2]:
                return True
            elif v1[2] < v2[2]:
                return False
            else:
                False

def get_all_official_model_path(suffix_set, ignore_dir_set):
    # official
    official_model_list = []
    svn_download_command = f"svn list {SVN_ROOT} --username {SVN_USERNAME} --password {SVN_PASSWORD} -R"
    result = subprocess.run(svn_download_command, shell=True, check=True, text=True, capture_output=True).stdout
    
    result = result.split("\n")
    for each_model_path in result:
        if not each_model_path:
            continue

        # ignore dir
        ignore = False
        for each_ignore_dir in ignore_dir_set:
            if each_model_path.startswith(each_ignore_dir):
                ignore = True
                print(each_model_path)
                break

        if ignore:
            continue

        if os.path.splitext(each_model_path)[1] in suffix_set:
            official_model_list.append(each_model_path)
    return official_model_list

def get_all_customer_model_path(suffix_set):
    # customer
    customer_model_list = []
    for each_model_path in FileOperationUtil.re_all_file(MODEL_CUSTOMER_DIR, endswitch=list(suffix_set)):
        each_model_path = each_model_path[len(MODEL_CUSTOMER_DIR):].lstrip("/")
        customer_model_list.append(each_model_path)
    return customer_model_list

@model_router.get("/check/official")
async def check_model_official():
    # 返回所有的模型路径信息
    official_model_list = get_all_official_model_path(MODEL_SUFFIX_SET, SVN_IGNORE_DIR)
    log.info(f"* check official")
    return official_model_list

@model_router.get("/check/customer")
async def check_model_customer():
    # 返回所有的模型路径信息
    customer_model_list = get_all_customer_model_path(MODEL_SUFFIX_SET)
    log.info(f"* check customer")
    return customer_model_list

@model_router.get("/get_model_list")
async def get_model_list():
    # 展示模型和对应的各个版本，最好有最新的版本
    error_model_path_list = []
    model_info = {} # {"model_name":[version:[model_file_path]})]}

    need_file_suffix = set()
    need_file_suffix.update(MODEL_CONFIG_SIFFIX)
    need_file_suffix.update(MODEL_SUFFIX_SET)
    need_file_suffix.update(MODEL_TRAIN_SUFFIX)

    official_model_path_list = get_all_official_model_path(need_file_suffix, SVN_IGNORE_DIR)
    for each_path in official_model_path_list:
        model_name, model_version, model_file_name = get_model_name_and_version_from_svn_url(each_path)
        
        if model_name is not None:
            if model_name not in model_info:
                model_info[model_name] = {model_version:[model_file_name]}
            else:
                if model_version in model_info[model_name]:
                    model_info[model_name][model_version].append(model_file_name)
                else:
                    model_info[model_name][model_version] = [model_file_name] 
        else:
            error_model_path_list.append(each_path)
    log.info("* get_model_list")
    return {"error_model_path": error_model_path_list, "model_list": model_info}

@model_router.get("/load/official/{model_path:path}")
async def load_model(model_path:str):

    model_suffix = os.path.splitext(model_path)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model_name suffix must in {MODEL_SUFFIX_SET}")
    
    model_dir, model_name   = os.path.split(model_path)
    save_model_dir          = os.path.join(TEMP_DIR, model_dir)
    model_save_path         = f"{save_model_dir}/{model_name}"

    if os.path.exists(model_save_path):
        log.error(f"* load offocial : {model_path}")
        return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
    else:
        os.makedirs(save_model_dir, exist_ok=True)
        svn_download_command = f"svn export {SVN_ROOT}/{model_path} {model_save_path} --username txkj --password txkj"
        try:
            subprocess.run(svn_download_command, shell=True, check=True)
            log.info(f"* load offocial : {model_path}")
            return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
        except subprocess.CalledProcessError as e:
            log.error(f"* download from SVN failed : {model_path} , error : {e}")
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
        log.info(f"* load model : {model_path}")
        return FileResponse(model_save_path, media_type = "application/octet-stream", filename=model_name)
    else:
        log.error(f"* load model info failed, model path not exists : {model_path}")
        return HTTPException(status_code=500, detail=f"model path not exists : {model_path}")
    
@model_router.get("/delete/{model_name:path}")
async def delete_model(model_name:str):

    model_suffix = os.path.splitext(model_name)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        return HTTPException(status_code=500, detail=f"model suffix must in {MODEL_SUFFIX_SET}")

    model_path = os.path.join(MODEL_CUSTOMER_DIR, model_name)

    if os.path.exists(model_path):
        os.remove(model_path)
        log.info(f"* delete dataset success : {model_path}")
        return {"status": f"* delete dataset success : {model_path}"}
    else:
        log.error(f"{model_path} not exists in model customer dir")
        return HTTPException(status_code=500, detail=f"{model_path} not exists in model customer dir")

@model_router.post("/upload/{model_name:path}")
async def upload_model(model_name:str, file: UploadFile = File(...)):

    model_suffix = os.path.splitext(model_name)[1]
    if model_suffix not in MODEL_SUFFIX_SET:
        log.error(f"* upload model failed : model suffix must in {MODEL_SUFFIX_SET}")
        return HTTPException(status_code=500, detail=f"model suffix must in {MODEL_SUFFIX_SET}")

    save_model_path = os.path.join(MODEL_CUSTOMER_DIR, model_name)
    contents = await file.read()

    if os.path.exists(save_model_path):
        log.error(f"* upload model failed : {model_name} exists, change a new name")
        return HTTPException(status_code=500, detail=f"{model_name} exists, change a new name")
    else:
        save_model_folder = os.path.split(save_model_path)[0]
        os.makedirs(save_model_folder, exist_ok=True)

        with open(save_model_path, "wb") as f:
            f.write(contents)
        log.info(f"* upload model success : {model_name}")
        return {"status": "success", "message": "upload model success"}



# TODO: load_model, 提供的是 svn 地址，或者模型的 md5

# TODO: 已经下载的模型在本地应该有缓存

# TODO: 注册模型，上传模型文件，上传配置文件，上传测试图片，上传测试结果图片，测试模型按照一定的配置是否能测试成功，成功的话结果写到 redis 中

# TODO: 注册好的模型可以直接使用 http 进行模型之间的交流，速度可能会慢一点，但是不需要本地有运行的环境

# TODO: 平台可以（1）加载一个模型 （2）卸载一个模型 （3）测试一个模型 （4）对模型实时修改配置 （5）查看模型的状态，模型自测



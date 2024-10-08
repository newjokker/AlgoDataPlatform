
import os
from fastapi import APIRouter, UploadFile, File
from JoTools.utils.FileOperationUtil import FileOperationUtil
from config import UCD_APP_DIR
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from JoTools.utils.LogUtil import LogUtil
from config import LOG_DIR, APP_LOG_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "menu", print_to_console=False)



menu_router = APIRouter(prefix="/menu", tags=["menu"])


@menu_router.get("/")
def show_stastic_labels():
    return {"info": "这是导航界面，还没有开发出来"}



# 导航页面，用于展示其他的页面的一些信息，不用记得所有的 路径




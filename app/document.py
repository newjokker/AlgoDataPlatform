

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
log = LogUtil.get_log(log_path, 5, "document", print_to_console=False)


doc_router = APIRouter(prefix="/doc", tags=["doc"])



# TODO: pingcode 的文档如何从外部读取， https://pingcode.tuxingkeji.com/open

# TODO: 将文档也整合进来

# TODO: 现在很多数据都存放在不同的地方找一个东西非常的难受，需要有一个统一的平台管理这些所有的数据



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(doc_router, host="0.0.0.0", port=12345)







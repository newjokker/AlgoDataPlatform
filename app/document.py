

import os
import time
import json
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.exceptions import HTTPException
from config import UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, r, REDIS_JSON_INFO
from JoTools.utils.FileOperationUtil import FileOperationUtil
from pydantic import BaseModel


doc_router = APIRouter(prefix="/doc", tags=["ucd"])


# TODO: pingcode 的文档如何从外部读取， https://pingcode.tuxingkeji.com/open

# TODO: 将文档也整合进来

# TODO: 现在很多数据都存放在不同的地方找一个东西非常的难受，需要有一个统一的平台管理这些所有的数据
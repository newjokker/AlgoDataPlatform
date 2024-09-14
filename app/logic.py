import os
from fastapi import APIRouter
from JoTools.utils.LogUtil import LogUtil
from config import LOG_DIR, APP_LOG_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "logic", print_to_console=False)



logic_router = APIRouter(prefix="/logic", tags=["logic"])

@logic_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

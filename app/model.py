from fastapi import APIRouter

model_router = APIRouter(prefix="/model", tags=["model"])

@model_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]



# TODO: 和 svn 进行联动，本地要存储一个缓存,没有缓存的话直接从 svn 上进行下载



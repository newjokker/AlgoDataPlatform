from fastapi import APIRouter

tag_router = APIRouter(prefix="/tag", tags=["tag"])

@tag_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

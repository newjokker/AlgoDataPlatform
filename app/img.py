from fastapi import APIRouter

img_router = APIRouter(prefix="/uc", tags=["img"])

@img_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

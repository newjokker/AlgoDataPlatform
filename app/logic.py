from fastapi import APIRouter

logic_router = APIRouter(prefix="/logic", tags=["logic"])

@logic_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

from fastapi import APIRouter

ucd_router = APIRouter(prefix="/ucd", tags=["ucd"])

@ucd_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

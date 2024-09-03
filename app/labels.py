from fastapi import APIRouter

label_router = APIRouter(prefix="/label", tags=["label"])

@label_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

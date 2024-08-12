from fastapi import APIRouter

model_router = APIRouter(prefix="/model", tags=["model"])

@model_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

from fastapi import APIRouter

app_router = APIRouter(prefix="/app", tags=["app"])

@app_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

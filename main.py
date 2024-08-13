
from fastapi import FastAPI
from app.img import img_router
from app.dataset import ucd_router
from app.app import app_router
from app.logic import logic_router
from app.model import model_router
from config import SERVER_HOST, SERVER_IP, SERVER_PORT


app = FastAPI()

app.include_router(img_router)
app.include_router(ucd_router)
app.include_router(app_router)
app.include_router(logic_router)
app.include_router(model_router)



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)



# TODO: 增加对应的日志，用于方便调试代码




from fastapi import FastAPI

from app.img import img_router
from app.dataset import ucd_router
from app.app import app_router
from app.logic import logic_router
from app.model import model_router

app = FastAPI()

app.include_router(img_router)
app.include_router(ucd_router)
app.include_router(app_router)
app.include_router(logic_router)
app.include_router(model_router)



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



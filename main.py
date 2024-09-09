

from config import SERVER_HOST, SERVER_PORT
from fastapi import FastAPI
from app.img import img_router
from app.dataset import ucd_router
from app.app import app_router
from app.logic import logic_router
from app.model import model_router
from app.document import doc_router
from app.tags import tag_router
from app.labels import label_router
from app.customerfile import customer_file_router
from app.menu import menu_router
from app.stastic import stastic_router


app = FastAPI()

app.include_router(img_router)
app.include_router(ucd_router)
app.include_router(app_router)
app.include_router(logic_router)
app.include_router(model_router)
app.include_router(doc_router)
app.include_router(tag_router)
app.include_router(label_router)
app.include_router(customer_file_router)
app.include_router(stastic_router)
app.include_router(menu_router)



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)






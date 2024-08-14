
from fastapi import FastAPI
from app.img import img_router
from app.dataset import ucd_router
from app.app import app_router
from app.logic import logic_router
from app.model import model_router
from app.document import doc_router

from config import SERVER_HOST, SERVER_PORT


app = FastAPI()

app.include_router(img_router)
app.include_router(ucd_router)
app.include_router(app_router)
app.include_router(logic_router)
app.include_router(model_router)
app.include_router(doc_router)



if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)



# TODO: 增加对应的日志，用于方便调试代码

# TODO: 将入库代码携程服务话的，这样就能更方便地去入库了，也解决了多个入口同时入库的问题

# TODO: UCD 之外写一个专门处理这个数据筛选的功能的可执行文件，所有的数据直接在服务器上进行筛选




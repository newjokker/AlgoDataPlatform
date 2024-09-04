from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import markdown2
import os
from JoTools.utils.LogUtil import LogUtil
from config import MYSQL_USER, LOG_DIR, MYSQL_PASSWORD, MYSQL_HOST, APP_LOG_NAME, MYSQL_DATABASE_NAME, MYSQL_TABLE_NAME


log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "labels", print_to_console=False)



label_router = APIRouter(prefix="/label", tags=["label"])


# TODO 先直接托管 .md 文件，使用网页的方式展示出来

# TODO: 还不如直接维护在 pingcode 上面，就是如何读取 pingcode 上面的信息，或者直接维护在 33 服务器上，直接使用 .md 的形式每次可以提交完善之后再去



@label_router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@label_router.get("/get_label_html/{label_name}")
async def get_label(label_name:str):
    # 将 label 转为 html 格式的网页进行返回

    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>FastAPI 表格示例</title>
        </head>
        <body>
            <h1>欢迎来到 FastAPI 表格示例页面</h1>
            <table border="1">
                <thead>
                    <tr>
                        <th>姓名</th>
                        <th>年龄</th>
                        <th>职业</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{label_name}</td>
                        <td>30</td>
                        <td>工程师</td>
                    </tr>
                    <tr>
                        <td>李四</td>
                        <td>25</td>
                        <td>设计师</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """

    markdown_text = """
# 标题

### 分级文本

#### 数据组管理标签
* 数据组难以在 ubuntu 上操作软件
* 数据组格式版本意识不强，最好能能硬性的要求，不符合要求无法通过
* 现在的各个标签没有地方进行管理和维护

#### 选择一种方式进行管理

（1）CI 流程去检查，文档是不是有问题
（2）写一个服务去管理文档，有标准化的接口，

#### 管理的粒度是标签
* 每一个标签有对应的独一无二的文档
* 每一个标签可以有对应的项目，模型等信息，这个会根据例行扫描任务自动更新
*最好写一个页面用于管理标签（1）上传 （2）更新 （3）删除 （4）查看，好处是方便做版本管理，

#### 现在我们在没有标签版本管理的情况下是如何做到下面两点的
* 如何确定新的标签名是不是重复的
* 找标注文档都在哪里找的

### 常问的数据的整体情况是什么（李智）

* ucd 工具熟练（网页服务，可视化界面）
* 数据存在哪里，模型存在哪里这些基础信息不清楚

![](http://192.168.3.111:11101/file/Egk0007.jpg)

    这是一段普通的文本。
    """

    html = markdown2.markdown(markdown_text)

    log.info(html)

    return HTMLResponse(content=html, status_code=200)



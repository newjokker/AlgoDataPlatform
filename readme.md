# 说明

### 镜像启动命令

* docker run -p 11101:11101 -p 11102:11102 -v /home/ldq/Data/ucd_app:/usr/data/ucd/app -v /home/ldq/Data/json_img:/usr/data/ucd/json_img -v /home/ldq/Data/official:/usr/data/ucd/official -v /home/ldq/Data/customer:/usr/data/ucd/customer -v /home/ldq/Data/temp:/usr/data/temp -v /home/ldq/Data/customer_model:/usr/data/model/customer --name ad_platform -d algo_data_platform:v0.1.5

### 镜像打包流程

* git clone ssh://git@192.168.3.108:2022/aigroup/algodataplatform.git

* docker build -t algo_data_platform:version -f Dockerfile . 

### 版本号码

* v0.0.x  初步实现数据平台，可视化只是个 demo

* v0.1.x  数据集展示功能基本实现可用


### TODO

* 写一个标签的服务，专门管理所有的标签。

* dockerfile 修改直接 gitclone 然后执行 dockerfile 就能打包，不需要修改文件路径之类的，不需要的文件可以增加 .dockerignore

* pingcode 集成进来

* 增加对应的日志，用于方便调试代码

* 将入库代码携程服务话的，这样就能更方便地去入库了，也解决了多个入口同时入库的问题

* UCD 之外写一个专门处理这个数据筛选的功能的可执行文件，所有的数据直接在服务器上进行筛选

* 增加相似图片查找的功能

* 增加已标注数据集管理功能，具体怎么管理还没想好


### 数据集可视化

* 将一个数据集进行可视化
* 加载一个数据集，展示有的 uc ，点击一个 uc 展示 uc 对应的图片和图片上对应的标签






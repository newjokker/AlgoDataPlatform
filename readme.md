# 说明

### 镜像启动命令

* docker run --name=algo_data_platform --volume=/home/ldq/Data:/usr/data  -v /etc/localtime:/etc/localtime  -p 11101:11101 -p 11102:11102 -p 11103:11103 -p 11104:11104 -p 11105:11105 -p 11106:11106  -d  algo_data_platform:v0.2.7


### 镜像打包流程

* git clone ssh://git@192.168.3.108:2022/aigroup/algodataplatform.git

* docker build -t algo_data_platform:version -f Dockerfile . 

### 版本号码

* v0.0.x  初步实现数据平台，可视化只是个 demo

* v0.1.x  数据集展示功能基本实现可用

* v0.2.x  增加 label 和 tag 相关的信息



### TODO

* 减少部署难度，启动 docker 就能新部署一套数据平台

* 新入库的数据的标签需要放在 数据库中

* 增加两个功能，标签可以被缓存到 redis 里面去，不一定会直接写到文件中，增加从文件中读取和存储到文件中的功能

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






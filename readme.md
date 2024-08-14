# 说明

### 镜像启动命令

* docker run -p 11101:11101 -v /home/ldq/Data/ucd_app:/usr/data/ucd/app -v /home/ldq/Data/json_img:/usr/data/ucd/json_img -v /home/ldq/Data/official:/usr/data/ucd/official -v /home/ldq/Data/customer:/usr/data/ucd/customer -v /home/ldq/Data/temp:/usr/data/temp -v /home/ldq/Data/customer_model:/usr/data/model/customer -d algo_data_platform:v0.0.4

### TODO

* 增加可视化界面

* pingcode 集成进来

* 增加对应的日志，用于方便调试代码

* 将入库代码携程服务话的，这样就能更方便地去入库了，也解决了多个入口同时入库的问题

* UCD 之外写一个专门处理这个数据筛选的功能的可执行文件，所有的数据直接在服务器上进行筛选



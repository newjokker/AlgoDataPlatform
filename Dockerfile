FROM ubuntu:latest


WORKDIR /usr/src/app


### redis
RUN apt-get update || true
RUN apt install redis -y && apt-get install supervisor -y
RUN sed -i '69s/.*/bind 127.0.0.1/' /etc/redis/redis.conf

# 安装 python 依赖包
RUN pip uninstall -y tensorboard & pip install tensorboard

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    redis \
    uvicorn \
    fastapi \
    JoUtil

# 拷贝模型文件
COPY ./data/models                          /usr/src/app/models

# 修改 train.py , dataloader.py
COPY ./data/app                     /usr/src/app
RUN  chmod 777 ./ -R
RUN  mkdir -p "/usr/src/app/runs" "/usr/src/app/runs/train" "/usr/src/app/runs/train_info"

# 安装 ucd
RUN mkdir -p /usr/ucd_cache
RUN /usr/src/app/ucd set cache_dir /usr/ucd_cache
RUN echo "alias ucd=/usr/src/app/ucd" > ~/.bash_aliases
RUN source ~/.bash_aliases

CMD ["./start_server.sh"]



# docker run --gpus device=0 -e TZ=Asia/Shanghai --shm-size=8g -p 6006:6006 --rm -v /home/suanfa-2/ucd_cache:/usr/ucd_cache -v /home/suanfa-2/ldq/YoloTrainServer/runs:/usr/scr/app/runs -d auto_yolo_train_server:v1.0.9 /bin/bash


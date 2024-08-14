FROM python:3.9.19

WORKDIR /usr/src/app

# redis
RUN apt-get update || true
RUN apt install redis -y && apt-get install supervisor -y && apt-get install vim -y 
RUN sed -i '69s/.*/bind 127.0.0.1/' /etc/redis/redis.conf

# 安装 python 依赖包
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    redis \
    uvicorn \
    fastapi \
    JoUtil \
    python-multipart 

# 修改 train.py , dataloader.py
COPY ./data/app                     /usr/src/app/app
COPY ./data/start_server.sh         /usr/src/app
COPY ./data/stop_server.sh          /usr/src/app
COPY ./data/main.py                 /usr/src/app
COPY ./data/confd.conf              /usr/src/app
COPY ./data/config.py               /usr/src/app
COPY ./data/ucd                     /usr/src/app

# 创建必要的文件夹
RUN mkdir -p /usr/src/app/logs

# 安装 ucd
RUN chmod 777 ~/ -R
RUN mkdir -p /usr/ucd_cache
RUN /usr/src/app/ucd set cache_dir /usr/ucd_cache
RUN echo "alias ucd=/usr/src/app/ucd" > ~/.bash_aliases

# 
CMD ["./start_server.sh"]



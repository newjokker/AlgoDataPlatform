FROM python:3.9.19

WORKDIR /usr/src/app

# redis
RUN apt-get update || true
RUN apt-get install libglib2.0-0 -y && apt install libgl1-mesa-glx -y && apt-get install gcc -y || true
RUN apt-get install vim -y && apt-get install supervisor -y && apt install redis -y 
RUN sed -i '69s/.*/bind 127.0.0.1/' /etc/redis/redis.conf

# 安装 python 依赖包
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    redis \
    uvicorn \
    fastapi \
    JoUtil \
    python-multipart \
    gradio

# 复制文件
COPY ./  /usr/src/app

# 创建必要的文件夹
RUN mkdir -p /usr/src/app/logs

# 安装 ucd
RUN chmod 777 ~/ -R
RUN mkdir -p /usr/ucd_cache
RUN /usr/src/app/tools/ucd set cache_dir /usr/ucd_cache
RUN echo "alias ucd=/usr/src/app/tools/ucd" > ~/.bash_aliases

# 
CMD ["./start_server.sh"]



FROM python:3.9.19

WORKDIR /usr/src/app

# install redis
RUN apt-get update || true
RUN apt-get install libglib2.0-0 -y && apt install libgl1-mesa-glx -y && apt-get install gcc -y || true
RUN apt-get install vim -y && apt-get install supervisor -y && apt install redis -y  
# RUN apt install wkhtmltopdf -y
RUN sed -i '69s/.*/bind 127.0.0.1/' /etc/redis/redis.conf

# install python package
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    redis \
    uvicorn \
    fastapi \
    JoUtil \
    python-multipart \
    gradio 

# copy file to image
COPY ./  /usr/src/app

# create dir 
RUN mkdir -p /usr/src/app/logs

# install ucd
RUN chmod 777 ~/ -R
RUN mkdir -p /usr/ucd_cache
RUN /usr/src/app/tools/ucd set cache_dir /usr/ucd_cache
RUN echo "alias ucd=/usr/src/app/tools/ucd" > ~/.bash_aliases

#  
CMD ["./start_server.sh"]



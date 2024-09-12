
import redis
import os


# common
DATA_DIR            = r"/usr/data"
# DATA_DIR            = r"/home/ldq/Data"
TEMP_DIR            = os.path.join(DATA_DIR, "temp")


# ucd
UCD_APP_DIR         = os.path.join(DATA_DIR, "ucd_app")         
UC_IMG_DIR          = os.path.join(DATA_DIR, "json_img")    
UCD_OFFICIAL_DIR    = os.path.join(DATA_DIR, "official")    
UCD_CUSTOMER_DIR    = os.path.join(DATA_DIR, "customer")    

# customer file
CUSTOMER_FILE_DIR   = os.path.join(DATA_DIR, "customer_file")  

# label
LABEL_DIR           = os.path.join(DATA_DIR, "labels")          

# redis
REDIS_HOST          = "127.0.0.1"
REDIS_PORT          = 6379
REDIS_JSON_INFO     = "ucd_json_info"
REDIS_MODEL_INFO    = "svn_model_info"

# server
SERVER_HOST         = "0.0.0.0"
# SERVER_PORT         = 21101
SERVER_PORT         = 11101
SERVER_LOCAL_HOST   = "127.0.0.1"

# svn
SVN_ROOT            = r"svn://192.168.3.101/repository"
SVN_USERNAME        = "txkj"
SVN_PASSWORD        = "txkj"
SVN_IGNORE_DIR      = {"基础镜像", "Other", "OTHER-专项"}

# model
MODEL_SUFFIX_SET    = {".pth", ".pt", ".model", ".plan", ".om"}
MODEL_TRAIN_SUFFIX  = {".json"}
MODEL_CONFIG_SIFFIX = {".ini"}
MODEL_CUSTOMER_DIR  = os.path.join(DATA_DIR, "model/customer")  


# ui server
UI_HOST             = "0.0.0.0"
UI_TAGS_PORT        = 11106
UI_LABELS_PORT      = 11105
UI_DATASET_PORT     = 11104
IMG_RESIZE_MAX      = 1500          # resize image 的时候允许的最长边的长度，不要修改，修改之后缓存数据需要清空

# Mysql
MYSQL_HOST                = "192.168.3.33"
MYSQL_PORT                = 3306
MYSQL_USER                = "root"
MYSQL_PASSWORD            = "root123"
MYSQL_DATABASE_NAME       = "SaturnTest"
MYSQL_TABLE_NAME          = "UcdJsonTag"

# log
LOG_DIR                 = "./logs"
UI_LOG_NAME             = "ui.log"
APP_LOG_NAME            = "app.log"

# stastic 
STASTIC_TAG_DIR         = os.path.join(DATA_DIR, "stastic/stastic_tags")   
STASTIC_LABEL_DIR       = os.path.join(DATA_DIR, "stastic/stastic_labels")  
STASTIC_SVN_MODEL_DIR   = os.path.join(DATA_DIR, "stastic/stastic_svn_model")  


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)





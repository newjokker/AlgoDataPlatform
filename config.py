
import redis

# common
TEMP_DIR            = r"/usr/data/temp"


# ucd
UCD_APP_DIR         = r"/usr/data/ucd/app"
UC_IMG_DIR          = r"/usr/data/ucd/json_img"
UCD_OFFICIAL_DIR    = r"/usr/data/ucd/official"
UCD_CUSTOMER_DIR    = r"/usr/data/ucd/customer"

# customer file
CUSTOMER_FILE_DIR   = r"/usr/data/customer_file"

# label
LABEL_DIR           = r"/usr/data/labels"

# redis
REDIS_HOST          = "127.0.0.1"
REDIS_PORT          = 6379
REDIS_JSON_INFO     = "ucd_json_info"
REDIS_MODEL_INFO    = "svn_model_info"

# server
SERVER_HOST         = "0.0.0.0"
SERVER_PORT         = 11106
SERVER_LOCAL_HOST   = "127.0.0.1"

# svn
SVN_ROOT            = r"svn://192.168.3.101/repository"
SVN_USERNAME        = "txkj"
SVN_PASSWORD        = "txkj"

# model
MODEL_SUFFIX_SET    = {".pth", ".pt", ".model", ".plan", ".om"}
MODEL_CUSTOMER_DIR  = r"/usr/data/model/customer"

# ui server
UI_HOST             = "0.0.0.0"
UI_TAGS_PORT        = 11105
UI_LABELS_PORT      = 11105
UI_DATASET_PORT     = 11101
IMG_RESIZE_MAX      = 1500          # resize image 的时候允许的最长边的长度，不要修改，修改之后缓存数据需要清空

# Mysql
MYSQL_HOST                = "192.168.3.33"
MYSQL_PORT                = 3306
MYSQL_USER                = "root"
MYSQL_PASSWORD            = "root123"
# MYSQL_DATABASE_NAME       = "Saturn_Database_V1"
MYSQL_DATABASE_NAME       = "SaturnTest"
MYSQL_TABLE_NAME          = "UcdJsonTag"

# log
LOG_DIR                 = "./logs"
UI_LOG_NAME             = "ui.log"
APP_LOG_NAME            = "app.log"

# stastic 
STASTIC_TAG_DIR         = "/usr/data/stastic/stastic_tags"




r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)





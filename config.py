
import redis

# common
TEMP_DIR            = r"/usr/data/temp"


# ucd
UCD_APP_DIR         = r"/home/ldq/Data/ucd_app"
# UCD_APP_DIR         = r"/usr/data/ucd/app"
UC_IMG_DIR          = r"/usr/data/ucd/json_img"
UCD_OFFICIAL_DIR    = r"/usr/data/ucd/official"
UCD_CUSTOMER_DIR    = r"/usr/data/ucd/customer"

# redis
REDIS_HOST          = "127.0.0.1"
REDIS_PORT          = 6379
REDIS_JSON_INFO     = "ucd_json_info"
REDIS_MODEL_INFO    = "svn_model_info"

# server
SERVER_HOST         = "0.0.0.0"
SERVER_PORT         = 11101

# svn
SVN_ROOT            = r"svn://192.168.3.101/repository"
SVN_USERNAME        = "txkj"
SVN_PASSWORD        = "txkj"

# model
MODEL_SUFFIX_SET    = {".pth", ".pt", ".model", ".plan", ".om"}
MODEL_CUSTOMER_DIR  = r"/usr/data/model/customer"


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)





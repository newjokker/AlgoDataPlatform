
import redis


# ucd
UCD_APP_DIR         = r"/home/ldq/Data/ucd_app"
UC_IMG_DIR          = r"/home/ldq/Data/json_img"
UCD_OFFICIAL_DIR    = r"/home/ldq/Data/official"
UCD_CUSTOMER_DIR    = r"/home/ldq/Data/customer"

# redis
REDIS_HOST      = "192.168.3.221"
REDIS_PORT      = 6379
REDIS_KEY       = "ucd_json_info2"

# server
SERVER_HOST     = "0.0.0.0"
SERVER_PORT     = 11101
SERVER_IP       = "192.168.3.50" 


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)





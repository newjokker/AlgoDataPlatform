from fastapi import APIRouter
from config import MYSQL_USER, LOG_DIR, MYSQL_PASSWORD, MYSQL_HOST, APP_LOG_NAME, MYSQL_DATABASE_NAME, MYSQL_TABLE_NAME
from fastapi.exceptions import HTTPException
import pymysql
from typing import List
from pydantic import BaseModel
import os

from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, APP_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "tags", print_to_console=False)


tag_router = APIRouter(prefix="/tag", tags=["tag"])


class AddTagInfo(BaseModel):
    tag_name:str
    tag_describe:str

class DeteteTag(BaseModel):
    tag_name: str

@tag_router.get("/get_tags")
def get_tag_info_from_mysql():
    tag_info = {} 
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,  
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME, 
            charset='utf8mb4', 
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            sql = f"SELECT * FROM {MYSQL_TABLE_NAME}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for each in rows:
                tag_info[each["tag"]] = each["tag_describe"]
        log.info("* get tag info from mysql")
        return {"status": "success", "tag_info": tag_info}  
    except pymysql.MySQLError as e:
        log.error(f"* Error while connecting to MySQL: {e}")
        # raise HTTPException(500, f"Error while connecting to MySQL: {e}")
        return {"status": "failed", "error_info": f"Error while connecting to MySQL: {e}"} 
    finally:
        if connection:
            connection.close()

@tag_router.post("/delete_tag")
def delete_tag_info_from_mysql(dete_tag:DeteteTag):
    tag_name = dete_tag.tag_name
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,  
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME, 
            charset='utf8mb4', 
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = f"DELETE FROM {MYSQL_TABLE_NAME} WHERE tag = %s"
            cursor.execute(sql, (tag_name,))
            connection.commit()
            log.info(f"* Tag '{tag_name}' has been deleted.")
            return {"status": "success"}

    except pymysql.MySQLError as e:
        connection.rollback()
        log.error(f"Error while deleting tag: {e}")
        return {"status": "failed", "error_info": f"Error while deleting tag: {e}"}
    finally:
        if connection:
            connection.close()
            # print("MySQL connection is closed")

@tag_router.post("/add_tag")
def add_tag_info_to_mysql(add_tag_info:AddTagInfo):

    tag_name = add_tag_info.tag_name
    tag_describe = add_tag_info.tag_describe

    if tag_describe == "":
        log.error("* tag_describe is empty")
        # raise HTTPException(500, "tag_name or tag_describe is empty")
        return {"status": "failed", "error_info": "tag_describe is empty"}

    if tag_name == "":
        log.info(f"* add tag failed, tag is empty : {tag_name}")
        # raise HTTPException(500, "tag_name is empty")
        return {"status": "failed", "error_info": "tag_name is empty"}

    if " " in tag_name:
        log.error("* have space in tag_name")
        # raise HTTPException(500, "have space in tag_name")
        return {"status": "failed", "error_info": "have space in tag_name"}

    if "," in tag_name:
        log.error("* have ',' in tag_name")
        # raise HTTPException(500, "have ',' in tag_name")
        return {"status": "failed", "error_info": "have ',' in tag_name"}

    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,  
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE_NAME, 
            charset='utf8mb4', 
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            check_sql = f"SELECT * FROM {MYSQL_TABLE_NAME} WHERE tag = %s"
            cursor.execute(check_sql, (tag_name,))
            existing_tag = cursor.fetchone()

            if existing_tag:
                log.error(f"* Tag '{tag_name}' already exists")
                return {"status": "failed", "error_info": f"Tag '{tag_name}' already exists"}

            sql = f"INSERT INTO {MYSQL_TABLE_NAME} (tag, tag_describe) VALUES (%s, %s)"
            cursor.execute(sql, (tag_name, tag_describe))
            connection.commit()
            log.info(f"* Tag '{tag_name}' has been added successfully")
            return {"status": "success"}

    except pymysql.MySQLError as e:
        connection.rollback()
        log.error(f"* Error while adding tag: {e}")
    finally:
        if connection:
            connection.close()

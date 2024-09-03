from fastapi import APIRouter
from config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE_NAME, MYSQL_TABLE_NAME
from fastapi.exceptions import HTTPException
import pymysql
from typing import List
from pydantic import BaseModel


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
        return tag_info
    except pymysql.MySQLError as e:
        print(f"Error while connecting to MySQL: {e}")
        raise HTTPException(500, f"Error while connecting to MySQL: {e}")
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
            print(f"* Tag '{tag_name}' has been deleted.")
    
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while deleting tag: {e}")
    finally:
        if connection:
            connection.close()
            # print("MySQL connection is closed")

@tag_router.post("/add_tag")
def add_tag_info_to_mysql(add_tag_info:AddTagInfo):

    tag_name = add_tag_info.tag_name
    tag_describe = add_tag_info.tag_describe

    if tag_name == "" or tag_describe == "":
        raise HTTPException(500, "tag_name or tag_describe is empty")

    if " " in tag_name:
        raise HTTPException(500, "have space in tag_name")

    if "," in tag_name:
        raise HTTPException(500, "have ',' in tag_name")

    if tag_name == "":
        print(f"* add tag failed, tag is empty : {tag_name}")
        raise HTTPException(500, "tag_name is empty")

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
            sql = f"INSERT INTO {MYSQL_TABLE_NAME} (tag, tag_describe) VALUES (%s, %s)"
            cursor.execute(sql, (tag_name, tag_describe))
            connection.commit()
            print(f"* Tag '{tag_name}' has been added successfully with ID {cursor.lastrowid}.")
            return {"status": "success"}

    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while adding tag: {e}")
    finally:
        if connection:
            connection.close()
            # print("MySQL connection is closed")


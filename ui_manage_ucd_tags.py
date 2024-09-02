# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import gradio as gr
import requests
import json
import yaml
from config import UI_PORT, UI_HOST, SERVER_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE_NAME
import socket
import os
import pymysql


HOST                    = "127.0.0.1"

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
            sql = "SELECT * FROM UcdJsonTag"
            cursor.execute(sql)
            rows = cursor.fetchall()

            for each in rows:
                tag_info[each["tag"]] = each["tag_describe"]
        return tag_info
    except pymysql.MySQLError as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection:
            connection.close()
            print("MySQL connection is closed")

def delete_tag_info_from_mysql(tag_name):
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
            sql = "DELETE FROM UcdJsonTag WHERE tag = %s"
            cursor.execute(sql, (tag_name,))
            connection.commit()
            if cursor.rowcount > 0:
                print(f"Tag '{tag_name}' has been deleted.")
            else:
                print(f"No tag found with name '{tag_name}'.")
    
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while deleting tag: {e}")
    finally:
        if connection:
            connection.close()
            print("MySQL connection is closed")

def add_tag_info_from_mysql(tag, description):
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
            sql = "INSERT INTO UcdJsonTag (tag, tag_describe) VALUES (%s, %s)"
            cursor.execute(sql, (tag, description))
            connection.commit()
            
            if cursor.lastrowid:
                print(f"Tag '{tag}' has been added successfully with ID {cursor.lastrowid}.")
            else:
                print(f"Failed to add tag '{tag}'.")
    
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while adding tag: {e}")
    finally:
        if connection:
            connection.close()
            print("MySQL connection is closed")

def get_cache_list():
    url = f"http://{HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    return official_ucd_list

def load_info_from_official_json(ucd_path):
    return load_info_from_json(ucd_path, is_official=True)

def load_info_from_customer_json(ucd_path):
    return load_info_from_json(ucd_path, is_official=False)

def load_info_from_json(ucd_path, is_official=True):
    file_type = "official" if is_official else "customer"
    url = f"http://{HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)
    # tags            = []
    count_tags_info = info.get("count_tags_info", {})
    file_size       = info.get("size", "null")
    uc_count        = info.get("uc_count", "null")
    add_time        = info.get("add_time", "null")
    tags            = info.get("tags", [])
    return_info  = f"add_time : {add_time}\nfile_size    : {file_size}\nuc_count : {uc_count}\nlabels:\n"
    # labels
    for each_tag in count_tags_info:
        return_info += f"    {each_tag} : {count_tags_info[each_tag]}\n"
    # tags
    return_tags = ""
    for each_tag in tags:
        return_tags += f"{each_tag},"
    return return_info, return_tags


official_ucd_list = get_cache_list()

tag_info = get_tag_info_from_mysql()


# 创建 Gradio 界面
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=7):
            official_uc_dataset_dd      = gr.Dropdown(choices=official_ucd_list, label="official uc dataset", allow_custom_value=True, value="")
            intensity_slider            = gr.Slider(minimum=0, maximum=100, step=1, value=50, label="uc slider", interactive=True)
            output_img=gr.Image(type='numpy', label="", height=700, width=1200)
            
        with gr.Column(scale=3):
            info_text           = gr.Textbox(label='Json Info', lines=5, placeholder="wait...", interactive=False)
            all_tags_dd         = gr.Dropdown(choices=list(tag_info.keys()), label="Select Tag", allow_custom_value=False, value="")
            tag_describe_text   = gr.Textbox(label='Tag Describe', lines=1, placeholder="", interactive=False)

            with gr.Row():
                add_tag_button  = gr.Button(value="Add Tag", min_width=1)
                del_tag_button  = gr.Button(value="Del Tag", min_width=1)
            
            tags_text           = gr.Textbox(label='Tags', lines=1, placeholder="", interactive=False)
            create_tag          = gr.Button(value='Create Tag', min_width=1)


    def update_dropdown_options():
        official_ucd_list = get_cache_list()
        return gr.Dropdown(choices=official_ucd_list, interactive=True, value="")

    official_uc_dataset_dd.change(
        fn=load_info_from_official_json,
        inputs=official_uc_dataset_dd,
        outputs=[info_text, tags_text]
    )


    # 为了快速展示图像信息，可以将 shape 信息先转化为 xml 信息，再生成一个不带 shape 的 json，这样的话每一次不用读取完整的 json 信息了


if __name__ == "__main__":


    # demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)
    demo.launch(server_name=UI_HOST, server_port=8089, share=False, debug=False)





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
            # print("MySQL connection is closed")

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
            print(f"Tag '{tag_name}' has been deleted.")
    
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while deleting tag: {e}")
    finally:
        if connection:
            connection.close()
            # print("MySQL connection is closed")

def add_tag_info_to_mysql(tag, description):

    if tag == "":
        print(f"* add tag failed, tag is empty : {tag}")
        return 

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
            print(f"Tag '{tag}' has been added successfully with ID {cursor.lastrowid}.")

    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"Error while adding tag: {e}")
    finally:
        if connection:
            connection.close()
            # print("MySQL connection is closed")

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

def get_tags_from_json():
    pass

def add_tag_to_json(ucd_name, tag_name):
    url = f"http://{HOST}:{SERVER_PORT}/ucd/add_tags"
    data = {"ucd_name": ucd_name, "is_official": True, "tags": [tag_name]}
    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)
    print(info)

def delete_tag_from_json():
    url = f"http://{HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)

official_ucd_list = get_cache_list()

global tag_info
tag_info = get_tag_info_from_mysql()


# 创建 Gradio 界面
with gr.Blocks() as demo:

    def show_tag_desc(tag_name):
        global tag_info
        if tag_name == "":
            return ""
        else:
            return tag_info[tag_name]

    def update_dropdown_options():
        official_ucd_list = get_cache_list()
        return gr.Dropdown(choices=official_ucd_list, interactive=True, value="")

    def create_tag(tag_name, tag_desc):
        add_tag_info_to_mysql(tag_name, tag_desc)
        global tag_info
        tag_info = get_tag_info_from_mysql()
        tags = list(tag_info.keys())
        if len(tags) == 0:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value="")
        else:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value=tags[0])

    def remove_tag_info(tag_name):
        delete_tag_info_from_mysql(tag_name)
        global tag_info
        tag_info = get_tag_info_from_mysql()
        tags = list(tag_info.keys())
        if len(tags) == 0:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value="")
        else:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value=tags[0])

    def add_tag_info(ucd_name, tag_name):
        add_tag_to_json(ucd_name, tag_name)


    with gr.Row():
        with gr.Column(scale=7):
            official_uc_dataset_dd      = gr.Dropdown(choices=official_ucd_list, label="official uc dataset", allow_custom_value=True, value="")
            intensity_slider            = gr.Slider(minimum=0, maximum=100, step=1, value=50, label="uc slider", interactive=True)
            output_img=gr.Image(type='numpy', label="", height=700, width=1200)
            
        with gr.Column(scale=3):
            info_text           = gr.Textbox(label='Json Info', lines=5, placeholder="wait...", interactive=False)
            tag_info_text       = gr.Textbox(label="Tag Info", lines=1, interactive=False)
            tags = list(tag_info.keys())
            if len(tags) == 0:
                select_tags_dd         = gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value="")
            else:
                select_tags_dd         = gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value=tags[0])
            tag_describe_text   = gr.Textbox(label='Tag Describe', lines=1, placeholder="", interactive=False, value=show_tag_desc(select_tags_dd.value))

            with gr.Row():
                add_tag_button  = gr.Button(value="Add Tag", min_width=1)
                del_tag_button  = gr.Button(value="Del Tag", min_width=1)
                rem_tag_button  = gr.Button(value="Remove Tag", min_width=1)
            
            tags_name_text      = gr.Textbox(label='Tag Name', lines=1, placeholder="", interactive=True)
            tags_des_text       = gr.Textbox(label='Tag Describe', lines=1, placeholder="", interactive=True)
            create_tag_button   = gr.Button(value='Create Tag', min_width=1)


    official_uc_dataset_dd.change(
        fn=load_info_from_official_json,
        inputs=[official_uc_dataset_dd],
        outputs=[info_text, tag_info_text]
    )
    create_tag_button.click(
        fn=create_tag,
        inputs=[tags_name_text, tags_des_text],
        outputs=[select_tags_dd],
    )

    select_tags_dd.change(
        fn=show_tag_desc,
        inputs=[select_tags_dd],
        outputs=[tag_describe_text],
    )

    rem_tag_button.click(
        fn=remove_tag_info,
        inputs=[select_tags_dd],
        outputs=[select_tags_dd],
    )

    add_tag_button.click(
        fn=add_tag_info,
        inputs=[official_uc_dataset_dd, select_tags_dd],
        # outputs=[tag_info_text],
    )



if __name__ == "__main__":

    # TODO: 标签的获取需要一个新的方式，需要直接读取文件，因为标签会经常变化，或者强制刷新 redis 的信息



    # demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)
    demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)



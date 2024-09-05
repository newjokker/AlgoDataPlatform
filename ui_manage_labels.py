# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import gradio as gr
import requests
import json
import yaml
from config import UI_TAGS_PORT, UI_HOST, SERVER_PORT, SERVER_LOCAL_HOST, LOG_DIR, UI_LOG_NAME, UI_LABELS_PORT
import socket
import os
import copy
from JoTools.utils.LogUtil import LogUtil
from app.tools import Label

log_path = os.path.join(LOG_DIR, UI_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "ui_manage_labels", print_to_console=False)


global now_label    # 当前的标签对象


global label_list 
response = requests.get("http://192.168.3.50:11106/label/get_labels")
label_info = json.loads(response.text)
label_list = label_info.get("labels", [])


def get_tag_info_from_mysql():
    url_get_tag_info    = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/get_tags"
    response = requests.get(url_get_tag_info)
    tag_info = json.loads(response.text)

    if tag_info["status"] == "success":
        log.info(f"* get tag info from mysql")
        return tag_info["tag_info"]
    else:
        log.error(f"* get tag info failed, error info : {tag_info['error_info']}")
        raise gr.Error(f"* get tag info failed, error info : {tag_info['error_info']}")

def add_tag_info_to_mysql(tag_name, tag_desc):
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/add_tag"
    data = {"tag_name": tag_name, "tag_describe": tag_desc}
    response = requests.post(url, json=data)
    response = json.loads(response.text)
    if response["status"] == "success":
        log.info(f"* add tag to mysql : {tag_name}")
        return response
    else:
        log.error(f"* add tag info failed, error info : {response['error_info']}")
        raise gr.Error(f"* add tag info failed, error info : {response['error_info']}")

def delete_tag_info_from_mysql(tag_name):
    url_delete_tag      = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/delete_tag"
    response = requests.post(url_delete_tag, json={"tag_name": tag_name})
    response = json.loads(response.text)

    if response["status"] == "success":
        log.info(f"* remove tag from mysql : {tag_name}")
        return response
    else:
        log.error(f"* remove tag info failed, error info : {response['error_info']}")
        raise gr.Error(f"* remove tag info failed, error info : {response['error_info']}")

def get_cache_list():
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    log.info(f"* get ucd name list from official")
    return official_ucd_list

def load_info_from_json(ucd_path, is_official=True):
    file_type = "official" if is_official else "customer"
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)
    log.info(f"* load info from json : {ucd_path}")
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
    return return_info, info


# 创建 Gradio 界面
with gr.Blocks() as demo:

    def show_label_info(label_name):
        global now_label   
        response = requests.get(f"http://192.168.3.50:11106/label/get_label_info/{label_name}")
        json_dict = json.loads(response.text)
        now_label = Label() 
        now_label.load_from_json_dict(json_dict)
        pic_des_list = [x[0] for x in now_label.pic_describe]
        log.info(list(now_label.attention))
        return now_label.save_to_html_str(), now_label.english_name, now_label.chinese_name, now_label.describe,\
            gr.Dropdown(choices=list(now_label.attention), label="Attention", interactive=True, allow_custom_value=True), \
            gr.Dropdown(choices=pic_des_list, label="Picture Describe", interactive=True, allow_custom_value=True)

    def update_english_name(name):
        global now_label
        now_label.english_name = name
    
    def update_chinese_name(name):
        global now_label
        now_label.chinese_name = name
    
    def update_describe(des):
        global now_label
        now_label.describe = des

    def add_assign_attention(attention):
        global now_label
        if attention in ["", " ", None]:
            raise gr.Error("attention can't be empty")

        now_label.add_attention(attention)
        return gr.Dropdown(label="Attention", interactive=True, allow_custom_value=True, choices=list(now_label.attention))
    
    def remove_assign_attention(attention):
        global now_label
        res  = now_label.remove_attention(attention)
        log.info(res)
        return gr.Dropdown(label="Attention", interactive=True, allow_custom_value=True, choices=list(now_label.attention))

    def update_html():
        global now_label
        return now_label.save_to_html_str()

    with gr.Row():
        
        with gr.Column(scale=5):
            label_html=gr.HTML()
            
        with gr.Column(scale=5):
            label_selected_dd   = gr.Dropdown(choices=label_list, label="Label Selected", allow_custom_value=False)
            
            with gr.Row():
                update_bt           = gr.Button("Update")
                save_bt             = gr.Button("Save")
                force_save_bt       = gr.Button("Force Save")

            english_name_text   = gr.Text(label="English Name", interactive=True)
            chinese_name_text   = gr.Text(label="Chinese Name", interactive=True)
            describe_text       = gr.Text(label="Describe", interactive=True)
            
            with gr.Row():
                with gr.Column(scale=8):
                    attention_dd        = gr.Dropdown(label="Attention", interactive=True, allow_custom_value=True)
                with gr.Column(scale=2):
                    add_attention_bt              = gr.Button(value="Add Attention", size="sm", min_width=1)
                    delete_attention_bt           = gr.Button(value="Delete Attention", size="sm", min_width=1)

            with gr.Row():
                with gr.Column(scale=6):
                    pic_des_dd              = gr.Dropdown(label="Picture Describe", interactive=True, allow_custom_value=True, scale=4)
                    pic_width               = gr.Dropdown(label="Pic Width", choices=[300, 400, 500, 600, 700, 800, 900, 1000], value=500, interactive=True)

                with gr.Column(scale=2):
                    pic_file                = gr.File(scale=1)

            with gr.Row():
                pic_add_bt              = gr.Button(value="Add Pic Info", size="sm", min_width=1)
                pic_delete_bt           = gr.Button(value="Delete Pic Info", size="sm", min_width=1)


        label_selected_dd.change(
            fn=show_label_info,
            inputs=[label_selected_dd],
            outputs=[label_html, english_name_text, chinese_name_text, describe_text, attention_dd, pic_des_dd]
        )

        update_bt.click(
            fn=update_html,
            outputs=[label_html]
        )

        english_name_text.change(
            fn=update_english_name,
            inputs=[english_name_text],
        )

        chinese_name_text.change(
            fn=update_chinese_name,
            inputs=[chinese_name_text]
        )

        describe_text.change(
            fn=update_describe,
            inputs=[describe_text]
        )

        add_attention_bt.click(
            fn=add_assign_attention,
            inputs=[attention_dd],
            outputs=[attention_dd],
        )

        delete_attention_bt.click(
            fn=remove_assign_attention,
            inputs=[attention_dd],
            outputs=[attention_dd]
        )


if __name__ == "__main__":

    log.info(f"* start server {UI_HOST}:{UI_TAGS_PORT}")
    demo.launch(server_name=UI_HOST, server_port=UI_LABELS_PORT, share=False, debug=False)



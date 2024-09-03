# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import gradio as gr
import requests
import json
import yaml
from config import UI_PORT, UI_HOST, SERVER_PORT, SERVER_LOCAL_HOST, LOG_DIR
import socket
import os
import copy
from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, "UI.log")
log = LogUtil.get_log(log_path, 5, "ui_manage_ucd_tags", print_to_console=False)


def get_tag_info_from_mysql():
    url_get_tag_info    = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/get_tags"
    response = requests.get(url_get_tag_info)
    tag_info = json.loads(response.text)
    return tag_info

def add_tag_info_to_mysql(tag_name, tag_desc):
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/add_tag"
    data = {"tag_name": tag_name, "tag_describe": tag_desc}
    response = requests.post(url, json=data)  
    return response 

def delete_tag_info_from_mysql(tag_name):
    url_delete_tag      = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/tag/delete_tag"
    response = requests.post(url_delete_tag, json={"tag_name": tag_name})
    return response

def get_cache_list():
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    return official_ucd_list

def load_info_from_json(ucd_path, is_official=True):
    file_type = "official" if is_official else "customer"
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
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
    return return_info, info

def get_tags_from_json():
    pass

def delete_tag_from_json():
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)

official_ucd_list = get_cache_list()

global origin_file_tags
origin_file_tags = set()

global json_file_tags
json_file_tags = set()

global select_ucd_name      # 选中的数据集的名字
select_ucd_name = ""

global tag_info
tag_info = get_tag_info_from_mysql()


# 创建 Gradio 界面
with gr.Blocks() as demo:

    def show_tag_desc(tag_name):
        global tag_info
        if tag_name == "":
            return ""
        else:
            if tag_name in tag_info:
                return tag_info[tag_name]
            else:
                return ""

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

    def add_tag_info(tag_name):
        global json_file_tags
        if tag_name != "":
            json_file_tags.add(tag_name)
        return ",".join(json_file_tags)

    def del_tag_info(tag_name):
        global json_file_tags
        if tag_name in json_file_tags:
            json_file_tags.remove(tag_name)

        global tag_info
        tags = list(json_file_tags.union(set(tag_info.keys())))
        return ",".join(json_file_tags), gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False)
     
    def update_tags_info_from_mysql():
        global tag_info
        tag_info = get_tag_info_from_mysql()
        tags = list(tag_info.keys())
        if len(tags) == 0:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value="")
        else:
            return gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value=tags[0])

    def save_tag_to_json(ucd_name):
        url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/update_tags"
        data = {"ucd_name": ucd_name, "is_official": True}
        global json_file_tags
        data["tags"] = list(json_file_tags)
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        return "save success"

    def load_info_from_official_json(ucd_name):
        json_info_str, json_info = load_info_from_json(ucd_name, is_official=True)

        global json_file_tags
        global tag_info
        global select_ucd_name
        global origin_file_tags

        if ucd_name != "":
            # 标签做了改变采取修改源文件
            if origin_file_tags != json_file_tags:
                save_tag_to_json(select_ucd_name)
                log.info(f"* Auto save tags -> json : {ucd_name}")

        json_file_tags = set(json_info["tags"])
        origin_file_tags = copy.deepcopy(json_file_tags)
        
        tags = list(json_file_tags.union(set(tag_info.keys())))
        select_ucd_name = ucd_name
        return json_info_str, ",".join(json_file_tags), gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False)


    with gr.Row():
        
        with gr.Column(scale=6):
            official_uc_dataset_dd      = gr.Dropdown(choices=official_ucd_list, label="official uc dataset")
            intensity_slider            = gr.Slider(minimum=0, maximum=100, step=1, value=50, label="uc slider", interactive=True)
            output_img=gr.Image(type='numpy', label="", height=700, width=1200)
            
        with gr.Column(scale=4):
            json_info_text      = gr.Textbox(label='Json Info', lines=5, placeholder="wait...", interactive=False)
            tag_info_text       = gr.Textbox(label="Tag Info", lines=1, interactive=False)
            tags = list(tag_info.keys())

            if len(tags) == 0:
                select_tags_dd          = gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value="")
            else:
                select_tags_dd          = gr.Dropdown(choices=tags, label="Select Tag", allow_custom_value=False, value=tags[0])
    
            tag_describe_text   = gr.Textbox(label='Tag Describe', lines=1, placeholder="", interactive=False, value=show_tag_desc(select_tags_dd.value))

            with gr.Row():
                add_tag_button  = gr.Button(value="Add Tag", min_width=1)
                del_tag_button  = gr.Button(value="Del Tag", min_width=1)
                # rem_tag_button  = gr.Button(value="Remove Tag", min_width=1)
                # get_tag_button  = gr.Button(value="Update Tags", min_width=1)
                save_tag_button  = gr.Button(value="Save To File", min_width=1)

            tags_name_text      = gr.Textbox(label='Tag Name', lines=1, placeholder="", interactive=True)
            tags_des_text       = gr.Textbox(label='Tag Describe', lines=1, placeholder="", interactive=True)
            create_tag_button   = gr.Button(value='Create Tag', min_width=1)


    official_uc_dataset_dd.change(
        fn=load_info_from_official_json,
        inputs=[official_uc_dataset_dd],
        outputs=[json_info_text, tag_info_text, select_tags_dd]
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

    add_tag_button.click(
        fn=add_tag_info,
        inputs=[select_tags_dd],
        outputs=[tag_info_text],
    )

    del_tag_button.click(
        fn=del_tag_info,
        inputs=[select_tags_dd],
        outputs=[tag_info_text, select_tags_dd]
    )

    save_tag_button.click(
        fn=save_tag_to_json,
        inputs=[official_uc_dataset_dd],
        outputs=[json_info_text],
    )


if __name__ == "__main__":

    # TODO: 当刚读取的标签和最后的标签不变的时候，不去修改

    # TODO: 增加一个对当前集合操作的 log

    # TODO: 获取文件大小，当文件大于 100M 不能进行属性操作

    log.info("* start server")

    # demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)
    demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)



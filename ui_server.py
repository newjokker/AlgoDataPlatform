
import gradio as gr
import requests
import json
import yaml
from config import UI_PORT, UI_HOST, SERVER_PORT
import socket
import os


def get_cache_list():
    url = f"http://{HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    customer_ucd_list = json.loads(response.text)["customer"]

    url = f"http://{HOST}:{SERVER_PORT}/model/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_model_list = json.loads(response.text)["official"]
    customer_model_list = json.loads(response.text)["customer"]
    return official_ucd_list, customer_ucd_list, official_model_list, customer_model_list

def load_info_from_official_json(ucd_path):
    return load_info_from_json(ucd_path, is_official=True)

def load_info_from_customer_json(ucd_path):
    return load_info_from_json(ucd_path, is_official=False)

def load_info_from_json(ucd_path, is_official=True):
    file_type = "official" if is_official else "customer"
    url = f"http://{HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    info = json.loads(response.text)
    tags            = []
    count_tags_info = info.get("count_tags_info", {})
    file_size       = info.get("size", "null")
    uc_count        = info.get("uc_count", "null")
    add_time        = info.get("add_time", "null")
    return_info  = f"add_time : {add_time}\nfile_size    : {file_size}\nuc_count : {uc_count}\ntags:\n"
    for each_tag in count_tags_info:
        return_info += f"    {each_tag} : {count_tags_info[each_tag]}\n"
        tags.append(each_tag)
    return return_info


# 创建 Gradio 界面
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            update_dataset_button   = gr.Button('UpDate Info')
            
            official_uc_dataset_dd           = gr.Dropdown(choices=[], label="official uc dataset", allow_custom_value=True, value="")
            customer_uc_dataset_dd           = gr.Dropdown(choices=[], label="customer uc dataset", allow_custom_value=True, value="")
            
            official_model_list_dd           = gr.Dropdown(choices=[], label="official model_list", allow_custom_value=True, value="")
            customer_model_list_dd           = gr.Dropdown(choices=[], label="customer model_list", allow_custom_value=True, value="")
            
            app_list_dd                      = gr.Dropdown(choices=[], label="app_list", allow_custom_value=True, value="")

        with gr.Column(scale=1):
            response_train = gr.Textbox(label='info', lines=15, placeholder="wait...", interactive=False)

    def update_dropdown_options():
        official_ucd_list, customer_ucd_list, official_model_list, customer_model_list = get_cache_list()
        return gr.Dropdown(choices=official_ucd_list, interactive=True, value=""), \
                gr.Dropdown(choices=customer_ucd_list, interactive=True, value=""), \
                gr.Dropdown(choices=official_model_list, interactive=True, value=""), \
                gr.Dropdown(choices=customer_model_list, interactive=True, value="")


    update_dataset_button.click(
            fn=update_dropdown_options,
            outputs=[official_uc_dataset_dd, customer_uc_dataset_dd, official_model_list_dd, customer_model_list_dd]
    )

    official_uc_dataset_dd.change(
        fn=load_info_from_official_json,
        inputs=official_uc_dataset_dd,
        outputs=[response_train]
    )

    customer_uc_dataset_dd.change(
        fn=load_info_from_customer_json,
        inputs=customer_uc_dataset_dd,
        outputs=[response_train]
    )


if __name__ == "__main__":

    HOST                    = "127.0.0.1"

    demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)


# TODO: 数据集可视化功能
# （1）选着对应的数据集可以直接查看图片和结果，在网页上展示出来 
# （2）可以操作选择需要看的标签进行筛选 
# （3）标签是实时画出来的远程画出来之后进行推送

# TODO: 数据集操作功能 （1）提供 ucd 的在线版本 （2）提供


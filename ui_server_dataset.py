
import gradio as gr
import requests
import json
import yaml
from config import UI_PORT, UI_HOST, SERVER_PORT, TEMP_DIR
import socket
import os
import random
from JoTools.utils.JsonUtil import JsonUtil

HOST                    = "127.0.0.1"
SERVER_PORT             = 11101
TEMP_DIR                = "./imgs"
UCD_OFFICIAL_DIR        = r"/home/ldq/Data/official"
UCD_CUSTOMER_DIR        = r"/home/ldq/Data/customer"
UC_IMG_DIR              = r"/home/ldq/Data/json_img"

def get_official_cache_list():

    global now_dataset_name
    now_dataset_name = "official"

    url = f"http://{HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    return gr.Dropdown(choices=official_ucd_list, label="dataset", interactive=True)

def get_customer_cache_list():

    global now_dataset_name
    now_dataset_name = "customer"

    url = f"http://{HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    customer_ucd_list = json.loads(response.text)["customer"]
    return gr.Dropdown(choices=customer_ucd_list, label="dataset", interactive=True)

def load_info_from_json(ucd_path):

    global now_dataset_name

    file_type = now_dataset_name
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
    return return_info, gr.Slider(minimum=0, maximum=int(uc_count)-1, step=1, value=0, label="Intensity", interactive=True)

def load_dataset_info(ucd_path):

    global now_dataset_name
    global now_uc_list

    if now_dataset_name == "official":
        ucd_path = os.path.join(UCD_OFFICIAL_DIR, ucd_path + ".json")
    else:
        ucd_path = os.path.join(UCD_CUSTOMER_DIR, ucd_path + ".json")

    json_info = JsonUtil.load_data_from_json_file(ucd_path)
    now_uc_list = json_info["uc_list"]
    return f"load dataset info success : {len(now_uc_list)}"

def get_img_path_by_uc(slider_index):
    global now_uc_list
    uc = now_uc_list[slider_index]

    img_path = os.path.join(UC_IMG_DIR, uc[:3], uc + ".jpg")
    return img_path

# 创建 Gradio 界面
with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column(scale=4):
            output_img=gr.Image(type='filepath', label="处理后的图片", value=r"imgs/Zzz01cv.png", height=600, width=1200)
        
        with gr.Column(scale=1):
            with gr.Row():
                official_bt    = gr.Button(value="Official", min_width=1)
                customer_bt    = gr.Button(value="Customer", min_width=1)
            dataset_info    = gr.Dropdown(label="dataset", choices=[])
            show_platform   = gr.Textbox(label='info', placeholder="", interactive=False, min_width=1, lines=22)

    with gr.Row():
        with gr.Column(scale=10):
            intensity_slider            = gr.Slider(minimum=0, maximum=100000, step=1, value=50, label="Intensity", interactive=True)
        # with gr.Column(scale=1):
        start_bt   = gr.Button('show', min_width=1)

    with gr.Row():
        a_bt        = gr.Button('load dataset', min_width=1)
        b_bt        = gr.Button('draw', min_width=1)
        last_bt     = gr.Button('last', min_width=1)
        next_bt     = gr.Button('next', min_width=1)


    def click_last_bt(slider_index):
        slider_index -= 1
        uc_path = get_img_path_by_uc(slider_index)
        return uc_path, slider_index
    
    def click_next_bt(slider_index):
        slider_index += 1
        uc_path = get_img_path_by_uc(slider_index)
        return uc_path, slider_index

    last_bt.click(
        fn=click_last_bt,
        inputs=[intensity_slider],
        outputs=[output_img, intensity_slider]
    )

    next_bt.click(
        fn=click_next_bt,
        inputs=[intensity_slider],
        outputs=[output_img, intensity_slider]
    )

    intensity_slider.change(
        fn=get_img_path_by_uc,
        inputs=[intensity_slider],
        outputs=[output_img]
    )

    official_bt.click(
        fn=get_official_cache_list,
        outputs=[dataset_info]
    )

    customer_bt.click(
        fn=get_customer_cache_list,
        outputs=[dataset_info]
    )

    dataset_info.change(
        fn=load_info_from_json,
        inputs=[dataset_info],
        outputs=[show_platform, intensity_slider]
    )

    a_bt.click(
        fn=load_dataset_info,
        inputs=[dataset_info],
        outputs=[show_platform]
    )

    # 为了快速展示图像信息，可以将 shape 信息先转化为 xml 信息，再生成一个不带 shape 的 json，这样的话每一次不用读取完整的 json 信息了


if __name__ == "__main__":

    HOST                    = "127.0.0.1"
    SERVER_PORT             = 11101

    global now_dataset_name
    global now_uc_list

    now_uc_list = []
    now_dataset_name = "customer"

    img_list = os.listdir("./imgs")

    # TODO: 加载的时候就获取所有可以展示的数据集，直接放到 dropdown 里面去


    # demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)
    demo.launch(server_name=UI_HOST, server_port=8089, share=False, debug=False)


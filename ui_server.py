
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
        with gr.Column(scale=3):
            update_dataset_button   = gr.Button('UpDate Info')
            
            official_uc_dataset_dd      = gr.Dropdown(choices=[], label="official uc dataset", allow_custom_value=True, value="")
            customer_uc_dataset_dd      = gr.Dropdown(choices=[], label="customer uc dataset", allow_custom_value=True, value="")
            
            official_model_list_dd      = gr.Dropdown(choices=[], label="official model_list", allow_custom_value=True, value="")
            customer_model_list_dd      = gr.Dropdown(choices=[], label="customer model_list", allow_custom_value=True, value="")
            
            app_list_dd                 = gr.Dropdown(choices=[], label="app_list", allow_custom_value=True, value="")
            # intensity_slider            = gr.Slider(minimum=0, maximum=100, step=1, value=50, label="Intensity", info="info", interactive=True)


            with gr.Row():
                with gr.Column(scale=10):
                    intensity_slider            = gr.Slider(minimum=0, maximum=100000, step=1, value=50, label="Intensity", interactive=True)
                # with gr.Column(scale=1):
                start_bt   = gr.Button('show', min_width=1)

            with gr.Row():
                a_bt   = gr.Button('load all img', min_width=1)
                b_bt   = gr.Button('draw', min_width=1)
                last_bt   = gr.Button('last', min_width=1)
                next_bt   = gr.Button('next', min_width=1)


        with gr.Column(scale=5):
            outputs=gr.Image(type='filepath', label="处理后的图片", value=r"imgs/Zzz01cv.png"),
            response_train = gr.Textbox(label='info', lines=5, placeholder="wait...", interactive=False)


    def update_dropdown_options():
        official_ucd_list, customer_ucd_list, official_model_list, customer_model_list = get_cache_list()
        return gr.Dropdown(choices=official_ucd_list, interactive=True, value=""), \
                gr.Dropdown(choices=customer_ucd_list, interactive=True, value=""), \
                gr.Dropdown(choices=official_model_list, interactive=True, value=""), \
                gr.Dropdown(choices=customer_model_list, interactive=True, value="")

    def change_slider(value):
        return str(value)


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

    last_bt.click(
        fn=lambda x : x-1,
        inputs=[intensity_slider],
        outputs=[intensity_slider]
    )

    next_bt.click(
        # 如何提前将周围的几张图片全部下载下来，缓存下来进行处理
        fn=lambda x : x+1,
        inputs=[intensity_slider],
        outputs=[intensity_slider]
    )


    # 为了快速展示图像信息，可以将 shape 信息先转化为 xml 信息，再生成一个不带 shape 的 json，这样的话每一次不用读取完整的 json 信息了


if __name__ == "__main__":

    HOST                    = "127.0.0.1"

    # demo.launch(server_name=UI_HOST, server_port=UI_PORT, share=False, debug=False)
    demo.launch(server_name=UI_HOST, server_port=8089, share=False, debug=False)


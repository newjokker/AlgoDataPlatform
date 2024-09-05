# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import gradio as gr
import requests
import json
from config import UI_TAGS_PORT, UI_HOST, SERVER_PORT, SERVER_LOCAL_HOST, LOG_DIR, UI_LOG_NAME, UI_LABELS_PORT
import os
from JoTools.utils.LogUtil import LogUtil
from app.tools import Label

log_path = os.path.join(LOG_DIR, UI_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "ui_manage_labels", print_to_console=False)


global now_label    # 当前的标签对象


global label_list 
response = requests.get("http://192.168.3.50:11106/label/get_labels")
label_info = json.loads(response.text)
label_list = label_info.get("labels", [])
log.info(label_list)


# 创建 Gradio 界面
with gr.Blocks() as demo:

    def show_label_info(label_name):
        global now_label   
        response = requests.get(f"http://192.168.3.50:11106/label/get_label_info/{label_name}")
        json_dict = json.loads(response.text)
        now_label = Label() 
        now_label.load_from_json_dict(json_dict)
        pic_index_list = list(range(len(now_label.pic_describe)))
        return now_label.save_to_html_str(), now_label.english_name, now_label.chinese_name, now_label.describe,\
            gr.Dropdown(choices=list(now_label.attention), label="Attention", interactive=True, allow_custom_value=True, value=""), \
            gr.Dropdown(choices=pic_index_list, label="Picture Index", interactive=True, allow_custom_value=True, value="")\
            
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

    def show_pic_info(pic_index):
        global now_label
        return now_label.pic_describe[int(pic_index)][0]
         
    def update_pic_info(pic_index, pic_des, pic_path, pic_width):
        
        if pic_index in [None, "None"]:
            raise gr.Error(f"pic_index : {pic_index}")
        
        global now_label
        image_info = {}
        if pic_width in [None, "None"]:
            image_info = None
        else:
            image_info = {"width": int(pic_width)}
        now_label.update_pic_info(int(pic_index), pic_des=pic_des, pic_path=pic_path, image_info=image_info)
        return now_label.save_to_html_str()

    def add_pic_info(pic_des, img_path, pic_width):
        global now_label

        if pic_width in [None, ""]:
            image_info = {}
        else:
            image_info = {"width": int(pic_width)}

        if pic_des in [None, "None"]:
            raise gr.Error("pic des is empty")

        suffix = os.path.splitext(str(img_path))[1]
        if suffix not in [".jpg", ".JPG", ".png", ".PNG"]:
            raise gr.Error('file suffix not in : [".jpg", ".JPG", ".png", ".PNG"]')

        if not os.path.exists(str(img_path)):
            raise gr.Error("img_path not exist, please upload image")
        
        now_label.add_pic_describe(pic_des, img_path, image_info)
        pic_index_list = list(range(len(now_label.pic_describe)))
        return now_label.save_to_html_str(), gr.Dropdown(label="Pic Index", choices=pic_index_list), None

    def remove_pic_info(pic_index):
        global now_label
        if pic_index in ["None", None]:
            raise gr.Error(f"pic_index is : {pic_index}")

        if int(pic_index) >= len(now_label.pic_describe):
            raise gr.Error("pic_index > length of pic_info")

        now_label.remove_pic_info(pic_index=int(pic_index))
        pic_index_list = list(range(len(now_label.pic_describe)))
        return now_label.save_to_html_str(), gr.Dropdown(label="Pic Index", choices=pic_index_list)

    def save_label_to_file():
        global now_label
        data = {"json_str": json.dumps(now_label.save_to_json_dict()), "new_label": False}
        response = requests.post("http://192.168.3.50:11106/label/save_label_info", json=data)
        log.info(response.text)
        response = json.loads(response.text)
        if response["status"] == "failed":
            raise gr.Error(f"save label failed : {response['error_info']}")

        response = requests.get("http://192.168.3.50:11106/label/get_labels")
        label_info = json.loads(response.text)
        label_list = label_info.get("labels", [])
        return gr.Dropdown(choices=label_list, label="Label Selected", allow_custom_value=False, interactive=True)
    
    def force_save_label_to_file():
        global now_label
        data = {"json_str": json.dumps(now_label.save_to_json_dict()), "new_label": True}
        response = requests.post("http://192.168.3.50:11106/label/save_label_info", json=data)
        log.info(response.text)
        response = json.loads(response.text)
        if response["status"] == "failed":
            raise gr.Error(f"save label failed : {response['error_info']}")

        response = requests.get("http://192.168.3.50:11106/label/get_labels")
        label_info = json.loads(response.text)
        label_list = label_info.get("labels", [])
        return gr.Dropdown(choices=label_list, label="Label Selected", allow_custom_value=False, interactive=True)

    def update_html():
        global now_label
        return now_label.save_to_html_str()

    with gr.Row():
        
        with gr.Column(scale=4):
            label_html=gr.HTML()
            
        with gr.Column(scale=6):
            label_selected_dd   = gr.Dropdown(choices=label_list, label="Label Selected", allow_custom_value=False, interactive=True)
            
            with gr.Row():
                update_bt           = gr.Button("Update")
                save_bt             = gr.Button("Save")
                force_save_bt       = gr.Button("Force Save")

            english_name_text   = gr.Text(label="English Name", interactive=True)
            chinese_name_text   = gr.Text(label="Chinese Name", interactive=True)
            describe_text       = gr.Text(label="Describe", interactive=True)
            
            with gr.Row():
                with gr.Column(scale=10):
                    attention_dd        = gr.Dropdown(label="Attention", interactive=True, allow_custom_value=True)
                with gr.Column(scale=2):
                    add_attention_bt              = gr.Button(value="Add Attention", size="sm", min_width=1)
                    delete_attention_bt           = gr.Button(value="Delete Attention", size="sm", min_width=1)

            with gr.Row():
                with gr.Column(scale=6):
                    with gr.Row():
                        pic_width_dd           = gr.Dropdown(label="Pic Width", choices=[300, 400, 500, 600, 700, 800, 900, 1000], interactive=True)
                        pic_index_dd           = gr.Dropdown(label="Pic Index", choices=[1,2,3,4,5]) 
                    pic_des_text            = gr.Text(label="Picture Describe", interactive=True, lines=2)

                with gr.Column(scale=2):
                    pic_file                = gr.File(scale=1)

            with gr.Row():
                pic_update_bt           = gr.Button(value="Update Pic Info", size="sm", min_width=1)
                pic_add_bt              = gr.Button(value="Add Pic Info", size="sm", min_width=1)
                pic_delete_bt           = gr.Button(value="Delete Pic Info", size="sm", min_width=1)


        label_selected_dd.change(
            fn=show_label_info,
            inputs=[label_selected_dd],
            outputs=[label_html, english_name_text, chinese_name_text, describe_text, attention_dd, pic_index_dd]
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

        pic_index_dd.change(
            fn=show_pic_info,
            inputs=[pic_index_dd],
            outputs=[pic_des_text]
        )

        pic_update_bt.click(
            fn=update_pic_info,
            inputs=[pic_index_dd, pic_des_text, pic_file, pic_width_dd],
            outputs=[label_html]
        )

        pic_add_bt.click(
            fn=add_pic_info,
            inputs=[pic_des_text, pic_file, pic_width_dd],
            outputs=[label_html, pic_index_dd, pic_file]
        )

        pic_delete_bt.click(
            fn=remove_pic_info,
            inputs=[pic_index_dd],
            outputs=[label_html, pic_index_dd]
        )

        save_bt.click(
            fn=save_label_to_file,
            outputs=[label_selected_dd]
        )

        force_save_bt.click(
            fn=force_save_label_to_file,
            outputs=[label_selected_dd] 
        )


if __name__ == "__main__":

    log.info(f"* start server {UI_HOST}:{UI_TAGS_PORT}")
    demo.launch(server_name=UI_HOST, server_port=UI_LABELS_PORT, share=False, debug=False)



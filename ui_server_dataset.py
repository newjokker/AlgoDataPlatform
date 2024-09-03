
import gradio as gr
import requests
import json
import shutil
import time
import random
from config import UI_HOST, LOG_DIR, UI_LOG_NAME, SERVER_LOCAL_HOST, SERVER_PORT, TEMP_DIR, UCD_CUSTOMER_DIR, UCD_OFFICIAL_DIR, UC_IMG_DIR, UI_DATASET_PORT, IMG_RESIZE_MAX
import os
from JoTools.utils.JsonUtil import JsonUtil
import cv2 
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.HashlibUtil import HashLibUtil
from PIL import Image
from prettytable import PrettyTable
from JoTools.utils.LogUtil import LogUtil

log_path = os.path.join(LOG_DIR, UI_LOG_NAME)
log = LogUtil.get_log(log_path, 5, "ui_server_dataset", print_to_console=False)


def get_image_size(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        return width, height

def load_img_if_not_exists(uc):
    url = f"http://192.168.3.111:11101/file/{uc}.jpg"

    save_dir = os.path.join(UC_IMG_DIR, uc[:3])
    os.makedirs(save_dir, exist_ok=True)
    save_img_path = os.path.join(save_dir, uc + ".jpg")

    if os.path.exists(save_img_path):
        return 

    response = requests.get(url)
    with open(save_img_path, 'wb') as file:
        file.write(response.content)

def get_official_cache_list():

    global now_dataset_name
    now_dataset_name = "official"

    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    official_ucd_list = json.loads(response.text)["official"]
    return gr.Dropdown(choices=official_ucd_list, label="dataset", interactive=True)

def get_customer_cache_list():

    global now_dataset_name
    now_dataset_name = "customer"

    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/check"
    response = requests.get(url, headers={'Content-Type': 'application/json'})
    customer_ucd_list = json.loads(response.text)["customer"]
    return gr.Dropdown(choices=customer_ucd_list, label="dataset", interactive=True)

def load_info_from_json(ucd_path):

    global now_dataset_name
    global color_dict

    color_dict = {}

    load_dataset_info(ucd_path=ucd_path)

    file_type = now_dataset_name
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/ucd/get_json_info/{file_type}/{ucd_path}"
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
        each_color = [random.randint(30, 255), random.randint(30, 255), random.randint(30, 255)]
        color_dict[each_tag] = each_color

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

def get_img_numpy_by_uc(slider_index, json_path):
    global now_uc_list
    global color_dict

    uc = now_uc_list[slider_index]

    # FIXME: 在 33 服务器的原始数据备份之后直接使用原始数据，这边就可以去掉了
    load_img_if_not_exists(uc)

    img_path = os.path.join(UC_IMG_DIR, uc[:3], uc + ".jpg")

    w, h = get_image_size(img_path)

    resize_img_dir = os.path.join(TEMP_DIR, "resize_img", uc[:3])
    os.makedirs(resize_img_dir, exist_ok=True)

    if now_dataset_name == "customer":
        json_path = os.path.join(UCD_CUSTOMER_DIR, json_path + ".json")
    else:
        json_path = os.path.join(UCD_OFFICIAL_DIR, json_path + ".json")

    json_name_md5 = HashLibUtil.get_str_md5(json_path)
    save_json_xml_dir = os.path.join(TEMP_DIR, "ucd_xml", json_name_md5)
    save_redize_img_dir = os.path.join(TEMP_DIR, "resize_img")
    os.makedirs(save_redize_img_dir, exist_ok=True)
    each_xml_path = os.path.join(save_json_xml_dir, uc + ".xml")
    
    if os.path.exists(each_xml_path):
        a = DeteRes(each_xml_path)
    else:
        a = DeteRes()

    ratio = 1
    if max(h, w) > IMG_RESIZE_MAX:
        if h > w:
            ratio = h / IMG_RESIZE_MAX
        else:
            ratio = w / IMG_RESIZE_MAX

        b = DeteRes()
        for each_obj in a:
            b.add_obj(int(each_obj.x1/ratio), int(each_obj.y1/ratio), int(each_obj.x2/ratio), \
                      int(each_obj.y2/ratio), conf=each_obj.conf, tag=each_obj.tag)

        resize_img_path = os.path.join(resize_img_dir, uc + ".jpg")
        if os.path.exists(resize_img_path):
            img_numpy = cv2.imread(resize_img_path)
        else:
            img_numpy = cv2.imread(img_path)
            img_numpy = cv2.resize(img_numpy, (int(w/ratio), int(h/ratio)))
            cv2.imwrite(resize_img_path, img_numpy)

        b.img_ndarry = img_numpy
        img_numpy = b.draw_dete_res(save_path="", color_dict=color_dict)
        img_numpy = cv2.cvtColor(img_numpy, cv2.COLOR_RGB2BGR)
    else:
        img_numpy = cv2.imread(img_path)
        a.img_ndarry = img_numpy
        img_numpy = a.draw_dete_res(save_path="", color_dict=color_dict)
        img_numpy = cv2.cvtColor(img_numpy, cv2.COLOR_RGB2BGR)

    info = f"{uc}\n"
    info += f"  weigth : {w}\n  height : {h}\n\n"

    info += f"{'tag'.ljust(8)}{'x1'.ljust(6)}{'y1'.ljust(6)}{'x2'.ljust(6)}{'y2'.ljust(6)}{'conf'.ljust(6)}\n"
    for each_info in a:
        info += f"{each_info.tag.ljust(8)}{str(each_info.x1).ljust(6)}{str(each_info.y1).ljust(6)}{str(each_info.x2).ljust(6)}{str(each_info.y2).ljust(6)}{format(each_info.conf, '.2f').ljust(6)}\n"

    return img_numpy, info

def save_json_to_xml(json_path):
    """默认使用之前的缓存，增加一个强制刷新的按钮，清空之前的缓存"""

    if now_dataset_name == "customer":
        json_path = os.path.join(UCD_CUSTOMER_DIR, json_path + ".json")
    else:
        json_path = os.path.join(UCD_OFFICIAL_DIR, json_path + ".json")

    json_info = JsonUtil.load_data_from_json_file(json_path)
    
    json_name_md5 = HashLibUtil.get_str_md5(json_path)

    save_json_xml_dir = os.path.join(TEMP_DIR, "ucd_xml", json_name_md5)
    os.makedirs(save_json_xml_dir, exist_ok=True)

    index = 1
    uc_count = 0
    start_time = time.time()

    if "shapes" in json_info:
        uc_count = len(json_info["uc_list"])
        for each_uc in json_info["shapes"]:
            index += 1
            dete_res = DeteRes()
            each_xml_path = os.path.join(save_json_xml_dir, each_uc + ".xml")

            if not os.path.exists(each_xml_path):
                for each_obj in json_info["shapes"][each_uc]:
                    if each_obj["shape_type"] == "rectangle":
                        each_conf = each_obj["conf"]
                        each_label = each_obj["label"]
                        x1, y1, x2, y2 = each_obj["points"][0][0], each_obj["points"][0][1],each_obj["points"][1][0], each_obj["points"][1][1]
                        dete_res.add_obj(x1, y1, x2, y2, conf=each_conf, tag=each_label)
                dete_res.save_to_xml(each_xml_path)

            if time.time() - start_time > 0.5:
                yield  f"progress : {index} / {uc_count}"
                start_time = time.time()

    yield gr.update(value=f"progress : {uc_count} / {uc_count}  finished")

def clear_json_xml(json_path):

    if now_dataset_name == "customer":
        json_path = os.path.join(UCD_CUSTOMER_DIR, json_path + ".json")
    else:
        json_path = os.path.join(UCD_OFFICIAL_DIR, json_path + ".json")
    
    json_name_md5 = HashLibUtil.get_str_md5(json_path)

    save_json_xml_dir = os.path.join(TEMP_DIR, "ucd_xml", json_name_md5)
    
    if os.path.exists(save_json_xml_dir):
        shutil.rmtree(save_json_xml_dir)
    return f"clear shape info (.xml) success"


with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column(scale=4):
            output_img=gr.Image(type='numpy', label="", height=700, width=1200)
        
        with gr.Column(scale=1):
            with gr.Row():
                official_bt     = gr.Button(value="Official", min_width=1)
                customer_bt     = gr.Button(value="Customer", min_width=1)
            dataset_info        = gr.Dropdown(label="dataset", choices=[])
            show_platform       = gr.Textbox(label='info', placeholder="", interactive=False, min_width=1, lines=24)

    with gr.Row():
        # choose_uc = gr.Dropdown(interactive=True, allow_custom_value=False)
        with gr.Column(scale=10):
            intensity_slider            = gr.Slider(minimum=0, maximum=100, step=1, value=50, label="uc slider", interactive=True)
        # with gr.Column(scale=1):
        load_shape_bt   = gr.Button('load shape info', min_width=1)
        clean_shape_bt   = gr.Button('clear shape info', min_width=1)

    intensity_slider.change(
        fn=get_img_numpy_by_uc,
        inputs=[intensity_slider, dataset_info],
        outputs=[output_img, show_platform]
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

    load_shape_bt.click(
        show_progress=True,
        fn=save_json_to_xml,
        inputs=[dataset_info],
        outputs=[show_platform]
    )

    clean_shape_bt.click(
        show_progress=True,
        fn=clear_json_xml,
        inputs=[dataset_info],
        outputs=[show_platform]
    )



if __name__ == "__main__":

    # TODO: gradio 加载宽度较大的图片的时候会自动进行裁剪，如何去掉这块
    # TODO: 增加选项直接查看某一个 UC 的图片的选项
    # TODO: 增加删除缓存的 resize 图片的选项

    global now_dataset_name
    global now_uc_list
    global color_dict

    now_uc_list = []
    now_dataset_name = "customer"
    color_dict = {}

    demo.launch(server_name=UI_HOST, server_port=UI_DATASET_PORT, share=False, debug=False)


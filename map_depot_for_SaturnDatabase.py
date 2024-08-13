# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import os
import shutil
import time
import cv2
import random
import numpy as np
import socket
import requests
import redis
import json
import argparse
from flask import Flask, Response, request, jsonify, send_file, abort
from JoTools.utils.HashlibUtil import HashLibUtil
from gevent import monkey
from gevent.pywsgi import WSGIServer
from JoTools.txkj.jsonInfo import JsonInfo
from JoTools.utils.JsonUtil import JsonUtil
from JoTools.utils.FileOperationUtil import FileOperationUtil
# from JoTools.txkj.ucDatasetUtil import UcDataset



monkey.patch_all()

app=Flask(__name__)





def assign_uc_in_ucd_json(ucd_path, assign_uc):

    print("* check : ", ucd_path, ", ", assign_uc)
    each_ucd_info = JsonUtil.load_data_from_json_file(ucd_path)

    for each_uc in each_ucd_info["uc_list"]:
        if each_uc == assign_uc:
            return True
    return False

@app.route("/ucd/check_assign_uc/<assign_uc>")
def check_ucdataset_with_assign_uc(assign_uc):
    """打印所有的 ucdataset，官方的或者非官方的"""
    ucd_dict = {"official":[], "customer":[]}

    # official
    for each_ucd in FileOperationUtil.re_all_file(ucd_official_dir, endswitch=['.json'], recurse=False):
        # 官方 ucd 可以分为不同文件夹

        print(each_ucd)

        if assign_uc_in_ucd_json(each_ucd, assign_uc):
            each_ucd_name = each_ucd[len(ucd_official_dir)+1:][:-5]
            ucd_dict["official"].append(each_ucd_name)

    # # customer
    # for each_ucd in FileOperationUtil.re_all_file(ucd_customer_dir, endswitch=['.json']):
    #     if assign_uc_in_ucd_json(each_ucd, assign_uc):
    #         each_ucd_name = each_ucd[len(ucd_customer_dir)+1:][:-5]
    #         ucd_dict["customer"].append(each_ucd_name)

    return jsonify(ucd_dict)

def get_json_file_info(file_path):
    info = get_json_file_info_from_redis(file_path)
    if info:
        return info
    else:
        return get_json_file_info_from_file(file_path)

def get_json_file_info_from_file(file_path):
    file_info = None
    if os.path.exists(file_path):

        with open(file_path, 'r', encoding="utf-8") as json_file:
            json_info = json.load(json_file)

        count_tags_info = {}
        if "shapes" in json_info:
            for each_uc in json_info["shapes"]:
                for each_obj in json_info["shapes"][each_uc]:
                    each_label = each_obj["label"]
                    if each_label in count_tags_info:
                        count_tags_info[each_label] += 1
                    else:
                        count_tags_info[each_label] = 1
            
        file_info = {
            "add_time": "",
            "dataset_name": "",
            "describe": "",
            "json_path": "",
            "label_used": "",
            "model_name": "",
            "model_version": "",
            "update_time": "",
        }

        for each in file_info:
            if each in json_info:
                value = json_info[each]
                file_info[each] = str(value)
            else:
                file_info[each] = "null"

        file_info["count_tags_info"] = count_tags_info

        if file_info["json_path"]:
            file_info["json_name"] = os.path.split(file_path)[1]
        else:
            file_info["json_name"] = ""

        if file_info["update_time"] and file_info["update_time"] != "-1.0":
            file_info["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(file_info["update_time"])))

        if file_info["add_time"] and file_info["add_time"] != "-1.0":
            file_info["add_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(file_info["add_time"])))

        if "uc_list" in json_info:
            file_info["uc_count"] = str(len(json_info["uc_list"]))
        else:
            file_info["uc_count"] = "0"

        file_info["size"] = f"{os.path.getsize(file_path)/(1024*1024):.2f} M"

    return file_info

def save_json_info_to_redis(json_info, file_path):
    try:
        json_info_str = json.dumps(json_info)
        r.hset("ucd_json_info", file_path, json_info_str)
    except:
        pass

def get_json_file_info_from_redis(file_path):
    """先在 redis 中查询文件缓存是否存在，不存在的话创建缓存文件"""
    try:
        info = r.hget("ucd_json_info", file_path)
        if info is None:
            json_info = get_json_file_info_from_file(file_path)
            save_json_info_to_redis(json_info, file_path)
            return json_info
        else:
            json_info = json.loads(info.decode("utf-8"))
        return json_info
    except Exception as e:
        return {}

@app.route("/ucd/check_assign_json/<path:assign_path>")
def check_ucdataset_with_assign_json(assign_path):
    """打印所有的 ucdataset，官方的或者非官方的"""
    assign_path = str(assign_path).strip('"')
    if not assign_path.endswith(".json"):
        assign_path += ".json"

    off_path = os.path.join(ucd_official_dir, assign_path)
    cus_path = os.path.join(ucd_customer_dir, assign_path)

    if os.path.exists(off_path):
        json_info = get_json_file_info(off_path)
        return jsonify(json_info)
    elif os.path.exists(cus_path):
        json_info = get_json_file_info(cus_path)
        return jsonify(json_info)
    else:
        return jsonify({"error": f"can't find json path : {off_path} and {cus_path}"})

# ----------------------------------------------------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='map depto')
    parser.add_argument('--port', dest='port', type=int, default=3232)
    parser.add_argument('--host', dest='host', type=str, default='0.0.0.0')
    parser.add_argument('--img_dir', dest='img_dir', type=str)
    parser.add_argument('--tmp_dir', dest='tmp_dir', type=str, default=r"./tmp")
    parser.add_argument('--use_cache', dest='use_cache', type=str, default="False")
    parser.add_argument('--ip', dest='ip', type=str)
    #
    args = parser.parse_args()
    return args

def print_config():
    print("-"*30)
    print(f'host        : {host}')
    print(f'port        : {port}')
    print(f'ip          : {ip}')
    print(f'img_dir     : {img_dir}')
    print(f'tmp_dir     : {tmp_dir}')
    print(f'use_cache :   {use_cache_dir}')
    print("-"*30)

def serv_start():
    global host, port
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()


if __name__ == '__main__':

    # TODO: 增加获取 tag 的功能，缓存放在 redis 服务器里面，这样就不用经常去获取了，可以指定为强制重新获取

    # TODO: 新上传一个文件，查询在 redis 中是否有对应的记录，有的话直接就删除


    r = redis.Redis(host='192.168.3.221', port=6379, db=0)

    args = parse_args()
    img_dir             = r"\\192.168.3.33\data_ucd\root_dir\json_img"
    ucd_official_dir    = r"\\192.168.3.33\data_ucd\root_dir\uc_dataset"
    ucd_customer_dir    = r"\\192.168.3.33\data_ucd\root_dir\ucd_customer"
    ucd_app_dir         = r"\\192.168.3.33\data_ucd\root_dir\ucd"
    # -----------------------------------------------------------------------------
    # 缓存文件夹列表，就是说随机缓存在下面几个文件夹下面
    cache_dir_tmp_list = [r"D:\json_img", r"F:\json_img", r"H:\json_img", r"E:\json_img"]
    cache_dir_list = list()
    for eachDir in cache_dir_tmp_list:
        if os.path.exists(eachDir):
            cache_dir_list.append(eachDir)
    use_cache_dir = eval(args.use_cache)
    # -----------------------------------------------------------------------------
    tmp_dir = args.tmp_dir
    host = args.host
    port = args.port
    ip = args.ip

    print_config()

    serv_start()        
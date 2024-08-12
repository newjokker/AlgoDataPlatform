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


@app.route("/file/<uc_suffix>")
def get_uc_file(uc_suffix):
    # 图片上传保存的路径
    if uc_suffix.endswith(".jpg"):
        img_path = os.path.join(img_dir, uc_suffix[:3], uc_suffix)
        print(img_path)

        # 查看当前文件夹中是否有
        find_cache = False
        for each_dir in cache_dir_list:
            cache_img_path = os.path.join(each_dir, uc_suffix[:3], uc_suffix)
            if os.path.exists(cache_img_path):
                img_path = cache_img_path
                find_cache = True

        # 没找到缓存直接复制一份并提供上传
        if (find_cache is False) and (use_cache_dir is True):
            random_save_dir = random.choice(cache_dir_list)
            save_cache_img_dir = os.path.join(random_save_dir, uc_suffix[:3])
            os.makedirs(save_cache_img_dir, exist_ok=True)
            save_cache_img_path = os.path.join(save_cache_img_dir, uc_suffix)
            shutil.copy(img_path, save_cache_img_path)
            img_path = save_cache_img_path

        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                image = f.read()
                resp = Response(image, mimetype="image/png")
                return resp
        else:
            print(f"* no such img path : {img_path}")
    elif uc_suffix.endswith(".xml"):
        xml_path = os.path.join(img_dir, uc_suffix[:3], uc_suffix[:-4] + ".json")
        if os.path.exists(xml_path):
            json_info = JsonInfo(json_path=xml_path)
            save_xml_path = os.path.join(tmp_dir, uc_suffix)
            json_info.save_to_xml(xml_path=save_xml_path)
            print(save_xml_path)
            with open(save_xml_path, 'rb') as f:
                xml_file = f.read()
                resp = Response(xml_file, mimetype="text/xml")
                return resp
        else:
            print(f"* no such json path : {xml_path}")
    elif uc_suffix.endswith(".json"):
        json_path = os.path.join(img_dir, uc_suffix[:3], uc_suffix)
        print(json_path)
        if os.path.exists(json_path):
            with open(json_path, 'rb') as f:
                json_file = f.read()
                resp = Response(json_file, mimetype="application/x-javascript")
                return resp
        else:
            print(f"* no such json path : {json_path}")
            return jsonify({"status": "error, no such file"}), 500
    else:
        return jsonify({"status": "error, no such file"}), 500

@app.route("/ucd/<path:ucd_name>")
def get_ucd_file(ucd_name):
    # 下载 ucDataset 文件
    # 检查官方ucd 中有没有，如果没有再去检查非官方的 ucd 是否有

    ucd_official_path = os.path.join(ucd_official_dir, ucd_name + ".json")
    ucd_customer_path = os.path.join(ucd_customer_dir, ucd_name + ".json")

    if os.path.exists(ucd_official_path):
        return send_file(ucd_official_path, as_attachment=True)
    elif os.path.exists(ucd_customer_path):
        return send_file(ucd_customer_path, as_attachment=True)
    else:
        return jsonify({"error": f"ucd_name : {ucd_name} not exists"}), 500

def get_version_list():
    version_list = []
    version_dict = {}

    for each_so_path in FileOperationUtil.re_all_file(ucd_app_dir):
        so_name = os.path.split(each_so_path)[1]
        print(so_name)
        version = so_name[4:]
        version_index_list = version[1:].split(".")
        version_index  = int(version_index_list[0]) * 1000000 + int(version_index_list[1]) * 1000 + int(version_index_list[2])
        version_dict[version_index] = version

    index_list = sorted(version_dict.keys())
    for each_index in index_list:
        version_str = version_dict[each_index]
        # so_path = os.path.join(ucd_app_dir, "libsaturntools_{0}.so".format(version_str))
        no_so_path = os.path.join(ucd_app_dir, "ucd_" + version_str)

        # 当 so 文件和对应的文件都存在的时候，才算一个版本
        if os.path.exists(no_so_path):
            version_list.append(version_dict[each_index])

    return version_list

@app.route("/ucd/ucd_version_list")
def get_ucd_version_list():
    """返回所有的在线版本"""
    version_list = get_version_list()
    return jsonify({"ucd_version_info":version_list})

@app.route("/ucd_app/<ucd_version>")
def get_ucd_app(ucd_version):
    ucd_app_path = os.path.join(ucd_app_dir, "ucd_" + ucd_version)

    print(ucd_app_path)

    if os.path.exists(ucd_app_path):
        return send_file(ucd_app_path, as_attachment=True)
    else:
        version_str = ",".join(get_version_list())
        return jsonify({"error": f"version should in : [{version_str}]"}), 500

@app.route("/ucd/check")
def check_ucdataset():
    """打印所有的 ucdataset，官方的或者非官方的"""
    ucd_dict = {"official":[], "customer":[]}

    # official
    for each_ucd in FileOperationUtil.re_all_file(ucd_official_dir, endswitch=['.json']):
        # 官方 ucd 可以分为不同文件夹
        each_ucd_name = each_ucd[len(ucd_official_dir)+1:][:-5]
        ucd_dict["official"].append(each_ucd_name)

    # customer
    for each_ucd in FileOperationUtil.re_all_file(ucd_customer_dir, endswitch=['.json']):
        each_ucd_name = each_ucd[len(ucd_customer_dir)+1:][:-5]
        ucd_dict["customer"].append(each_ucd_name)
    return jsonify(ucd_dict)

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

@app.route("/ucd/delete/<ucd_name>", methods=["DELETE"])
def delete_ucdataset(ucd_name):
    """打印所有的 ucdataset，官方的或者非官方的"""
    ucd_path = os.path.join(ucd_customer_dir, ucd_name)
    print(ucd_path)

    if os.path.exists(ucd_path):
        os.remove(ucd_path)
        return jsonify("ok"), 200
    else:
        return jsonify("ucd path not exists"), 500

@app.route("/ucd/upload", methods=["POST"])
def upload_ucdataset():
    """打印所有的 ucdataset，官方的或者非官方的"""
    if "ucd_name" in request.form:
        ucd_name = request.form["ucd_name"]
    else:
        return jsonify("ucd_name not exists"), 500

    file = request.files['json_file']
    
    if ucd_name.endswith(".json"):
        ucd_name = ucd_name[:-5]
        
    save_ucd_path = os.path.join(ucd_customer_dir, ucd_name + '.json')

    if os.path.exists(save_ucd_path):
        file.close()
        return jsonify("ucd_path exists, change a new name"), 500
    else:
        save_ucd_folder = os.path.split(save_ucd_path)[0]
        os.makedirs(save_ucd_folder, exist_ok=True)
        print(f"* save ucd path : {save_ucd_path}")
        file.save(save_ucd_path)
        file.close()

        # 新上传的文件在 redis 中删除对应的记录（如果有的话）
        try:
            r.hdel("ucd_json_info", save_ucd_path)
        except Exception as e:
            return jsonify({"error": e})

        return jsonify("ok"), 200

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
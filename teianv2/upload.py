from asyncio import tasks
import requests
import cv2
import logging
import numpy as np
# import mysql.connector
from flask import Flask, request, jsonify
from flask import render_template
from werkzeug.utils import secure_filename
from converter import i2b, b2i
import time
import threading

app = Flask(__name__)

exec_det_glo = [[1, 0], [2, 0], [3, 0]]
exec_dep_glo = [[1, 0], [2, 0], [3, 0]]
LOCK = threading.Lock()


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def uploads_file():

    all_time = time.time()

    # opencvでPOSTされたファイルを読み込む
    file_data = request.files['file'].read()
    nparr = np.fromstring(file_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # バイナリに変換
    img_b = i2b(img)

    load = time.time() - all_time

    # データサイズ
    size = len(img_b) / 1000000

    # 配置計算時間
    task_time1 = time.time()

    # 配置先決定
    # k = 0
    with LOCK:
        global exec_det_glo
        exec_det = exec_det_glo

        # for i in range(2):
        #     if exec_det[i][1] > exec_det[i+1][1]:
        #         k = exec_det[i+1]
        #         exec_det[i+1] = exec_det[i]
        #         exec_det[i] = k
    exec_det = sorted(exec_det, key=lambda x: x[1])
    select_task1 = exec_det[0][0]

    # 画像の送信
    url = "http://python-detection" + str(select_task1) + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    # 配置計算時間
    task_time1 = time.time() - task_time1

    # 実行時間計測
    detection = time.time()

    # 検知リクエスト
    response = requests.post(url, data=img_data)
    # detection_img = response.json()['data1']

    # 実行時間計測
    detection = time.time() - detection
    detection_size = detection/size

    exec_write1 = time.time()

    # 実行時間更新
    with LOCK:
        exec_det_glo[select_task1 - 1][1] = detection_size

    exec_write1 = time.time() - exec_write1
    # for i in range(3):
    #     if exec_det[i][0] == select_task1:
    #         exec_det[i][1] = detection

    # 配置計算時間
    task_time2 = time.time()

    # 配置先決定
    with LOCK:
        global exec_dep_glo
        exec_dep = exec_dep_glo
    # k = 0
    #    for i in range(2):
    #         if exec_dep[i][1] > exec_dep[i+1][1]:
    #             k = exec_dep[i+1]
    #             exec_dep[i+1] = exec_dep[i]
    #             exec_dep[i] = k

    exec_dep = sorted(exec_dep, key=lambda x: x[1])
    select_task2 = exec_dep[0][0]

    url = "http://python-depth" + str(select_task2) + ":8080/depth"

    task_time2 = time.time() - task_time2

    # 実行時間計測
    depth = time.time()

    # 距離推定リクエスト
    response = requests.post(url, data=img_data)
    # depth_img = response.json()['data2']

    # 実行時間計測
    depth = time.time() - depth
    depth_size = depth / size

    # 実行時間更新
    # with LOCK:
    # for i in range(3):
    #     if exec_dep[i][0] == select_task2:
    #         exec_dep[i][1] = depth

    exec_write2 = time.time()
    with LOCK:
        exec_dep_glo[select_task2 - 1][1] = depth_size
    exec_write2 = time.time() - exec_write2

    all_time = time.time() - all_time
    time_data = {
        "detection_pod": select_task1,
        "detection_time": detection,
        "detection_time_size": detection_size,
        "detection_calc_time": task_time1,
        "detection_update_time": exec_write1,
        "depth_pod": select_task2,
        "depth_time": depth,
        "depth_time_size": depth_size,
        "depth_calc_time": task_time2,
        "depth_update_time": exec_write2,
        "exec": all_time,
        "load_time": load
    }
    return jsonify(time_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)

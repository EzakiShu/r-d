import requests
import cv2
import logging
import numpy as np
import mysql.connector
from flask import Flask, request, jsonify
from flask import render_template
from werkzeug.utils import secure_filename
from converter import i2b, b2i
import time

app = Flask(__name__)

count = 0
pre_select_edge1 = 0
pre_select_edge2 = 0


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def uploads_file():

    all_time = time.time()

    global count
    count += 1

    # opencvでPOSTされたファイルを読み込む
    file_data = request.files['file'].read()
    nparr = np.fromstring(file_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # バイナリに変換
    img_b = i2b(img)

    # データサイズ
    size = len(img_b) / 1000000

    # database接続
    conn = mysql.connector.connect(
        host='mysql-server',
        port='3306',
        user='devuser',
        password='devuser',
        database='time'
    )
    cursor = conn.cursor(buffered=True)
    sql = ("SELECT * FROM detection")
    cursor.execute(sql)
    min_time_edge1 = cursor.fetchall()
    select_edge1 = min(
        min_time_edge1[0][1], min_time_edge1[1][1], min_time_edge1[2][1])

    global pre_select_edge1
    if pre_select_edge1 == select_edge1:
        select_edge1 = sorted(
            min_time_edge1[0][1], min_time_edge1[1][1], min_time_edge1[2][1])[2]

    pre_select_edge1 = select_edge1

    # 画像の送信
    url = "http://python-detection" + select_edge1 + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    # 実行時間計測
    detection = time.time()

    # 検知リクエスト
    response = requests.post(url, data=img_data)
    detection_img = response.json()['data1']

    # 実行時間計測
    detection = time.time() - detection
    detection /= size

    # DB更新
    sql = "UPDATE detection SET time=" + \
        str(detection) + "WHERE pod=detection'" + select_edge1 + "'"
    cursor.execute(sql)

    sql = ("SELECT * FROM depth")
    cursor.execute(sql)
    min_time_edge2 = cursor.fetchall()

    select_edge2 = min(
        min_time_edge2[0][1], min_time_edge2[1][1], min_time_edge2[2][1])

    global pre_select_edge2
    if pre_select_edge2 == select_edge2:
        select_edge2 = sorted(
            min_time_edge2[0][1], min_time_edge2[1][1], min_time_edge2[2][1])[2]

    pre_select_edge2 = select_edge2
    url = "http://python-depth" + select_edge2 + ":8080/depth"

    # 実行時間計測
    depth = time.time()

    # 距離推定リクエスト
    response = requests.post(url, data=img_data)
    depth_img = response.json()['data2']

    # 実行時間計測
    depth = time.time() - depth

    # DB更新
    sql = "UPDATE depth SET time=" + \
        str(depth) + "WHERE pod=depth'" + select_edge2 + "'"
    cursor.execute(sql)

    cursor.close()
    conn.commit()
    conn.close()

    all_time = time.time() - all_time
    time_data = {
        "detection_pod": select_edge1,
        "detection_time": detection,
        "depth_pod": select_edge2,
        "depth_time": depth,
        "exec": all_time,
        "count": count
    }
    return jsonify(time_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=False)

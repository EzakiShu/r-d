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


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def uploads_file():
    # 実行時間計測
    detection = time.time()

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
    sql = ("SELECT * FROM teian_detection")
    cursor.execute(sql)
    task1 = cursor.fetchall()

    time_estimate = [0.0, 0.0, 0.0]

    for i in range(3):
        hold = task1[i][2] - task1[i][3]
        time_estimate[i] = task1[i][1] * float(hold)

    min = 10000

    for i in range(3):
        if time_estimate[i] < min:
            min_edge1 = i + 1

    # 画像の送信
    url = "http://python-detection" + str(min_edge1) + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    sql = ("UPDATE teian_detection SET access = access + 1, time = " +
           str(time_estimate[i]) + "where pod=" + str(min_edge1))
    cursor.execute(sql)

    # 検知リクエスト
    response = requests.post(url, data=img_data)
    detection_img = response.json()['data1']

    # 実行時間計測
    detection = time.time() - detection
    detection /= size

    # DB更新
    sql = "UPDATE teian_detection SET fin = fin + 1, time=" + \
        str(detection) + "WHERE pod=" + str(min_edge1)
    cursor.execute(sql)

    # 実行時間計測
    depth = time.time()

    sql = ("SELECT * FROM teian_depth")
    cursor.execute(sql)
    task2 = cursor.fetchall()

    time_estimate = [0.0, 0.0, 0.0]

    for i in range(3):
        hold = task2[i][2] - task2[i][3]
        time_estimate[i] = task2[i][1] * float(hold)

    min = 10000

    for i in range(3):
        if time_estimate[i] < min:
            min_edge2 = i + 1

    url = "http://python-depth" + str(min_edge2) + ":8080/depth"

    sql = ("UPDATE teian_depth SET access = access + 1 where pod=" + str(min_edge2))
    cursor.execute(sql)

    # 距離推定リクエスト
    response = requests.post(url, data=img_data)
    depth_img = response.json()['data2']

    # 実行時間計測
    depth = time.time() - depth

    # DB更新
    sql = "UPDATE teian_depth SET fin = fin + 1, time=" + \
        str(depth) + "WHERE pod=" + str(min_edge2)
    cursor.execute(sql)

    cursor.close()
    conn.commit()
    conn.close()

    time_data = {
        "detection_pod": min_edge1,
        "detection_time": detection,
        "depth_pod": min_edge2,
        "depth_time": depth
    }
    return jsonify(time_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)

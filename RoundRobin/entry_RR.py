import requests
import cv2
import logging
import numpy as np
import mysql.connector
from flask import Flask, request
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

    # database接続
    conn = mysql.connector.connect(
        host='mysql-server',
        port='3306',
        user='devuser',
        password='devuser',
        database='time'
    )
    cursor = conn.cursor()
    sql = ("SELECT next FROM RoundRobin")
    cursor.execute(sql)
    next_edge = cursor.fetchone()

    # 画像の送信
    url = "http://python-detection" + str(next_edge[0]) + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    # 検知リクエスト
    response = requests.post(url, data=img_data)
    detection_img = response.json()['data1']

    # 実行時間計測
    detection = time.time() - detection

    # DB更新
    # sql = "UPDATE detection SET time=" + \
    #     str(detection) + "WHERE pod=depth'" + str(next_edge[0]) + "'"
    # cursor.execute(sql)

    # 実行時間計測
    depth = time.time()

    # 距離推定リクエスト
    url = "http://python-depth" + str(next_edge[0]) + ":8080/depth"
    response = requests.post(url, data=img_data)
    depth_img = response.json()['data2']

    # 実行時間計測
    depth = time.time() - depth

    # DB更新
    # sql = "UPDATE depth SET time=" + \
    #     str(depth) + "WHERE pod='" + str(next_edge[0]) + "'"
    # cursor.execute(sql)

    # next pod
    if next_edge[0] < 3:
        next = next_edge[0] + 1
    else:
        next = 1
    sql = "UPDATE RoundRobin SET next = " + str(next)

    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()

    img = '<img src="data:image/png;base64,' + detection_img + \
        '"/>' '<img src="data:image/png;base64,' + depth_img + '"/>'
    return img


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

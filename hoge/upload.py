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
    sql = ("SELECT pod FROM detection WHERE time=(SELECT MIN(time) FROM detection)")
    cursor.execute(sql)
    min_time_edge1 = cursor.fetchone()

    # 画像の送信
    url = "http://python-" + min_time_edge1[0] + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    # 検知リクエスト
    response = requests.post(url, data=img_data)
    detection_img = response.json()['data1']

    # 実行時間計測
    detection = time.time() - detection
    detection /= size

    # DB更新
    sql = "UPDATE detection SET time=" + \
        str(detection) + "WHERE pod='" + min_time_edge1[0] + "'"
    cursor.execute(sql)

    # 実行時間計測
    depth = time.time()

    sql = ("SELECT pod FROM depth WHERE time=(SELECT MIN(time) FROM depth)")
    cursor.execute(sql)
    min_time_edge2 = cursor.fetchone()

    url = "http://python-" + min_time_edge2[0] + ":8080/depth"

    # 距離推定リクエスト
    response = requests.post(url, data=img_data)
    depth_img = response.json()['data2']

    # 実行時間計測
    depth = time.time() - depth

    # DB更新
    sql = "UPDATE depth SET time=" + \
        str(depth) + "WHERE pod='" + min_time_edge2[0] + "'"
    cursor.execute(sql)

    cursor.close()
    conn.commit()
    conn.close()

    time_data = {
        "detection_pod": min_time_edge1[0],
        "detection_name": detection,
        "depth_pod": min_time_edge2[0],
        "depth_name": depth
    }
    return jsonify(time_data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)

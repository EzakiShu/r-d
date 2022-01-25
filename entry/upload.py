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

    # 処理時間測定
    start = time.time()

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
    min_time_edge = cursor.fetchone()

    # 画像の送信
    url = "http://python-" + min_time_edge[0] + ":8080/api/predict"
    img_data = {
        "data": img_b
    }

    # 転送時間計測
    #start = time.time()

    # 検知リクエスト
    response = requests.post(url, data=img_data)

    # 転送時間計測
    #end = time.time() - start
    #transfer_time = end - response.json()['time']
    #end /= size
    #transfer_time /= size

    # sql = "UPDATE detection SET time=" + \
    #     str(response.json()['time']) + \
    #     ",transfer=" + str(transfer_time) + " WHERE pod='" + \
    #     min_time_edge[0] + "'"

    # 処理時間測定
    end = time.time() - start
    end /= size

    sql = "UPDATE detection SET time=" + end + \
        " WHERE pod ='" + min_time_edge[0] + "'"
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()

    img = '<img src="data:image/png;base64,' + response.json()['data1'] + '"/>' \
        '<img src="data:image/png;base64,' + response.json()['data2'] + '"/>'
    #time = response.json()['time']
    # return str(time)
    return img


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

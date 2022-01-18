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

    # 転送時間計測
    #start = time.time()

    # 検知リクエスト
    response = requests.post(url, data=img_data)

    # 転送時間計測
    #end = time.time() - start
    #transfer_time = end - response.json()['time']

    # next pod
    if next_edge[0] == 1:
        next = "2 where next=1"
    elif next_edge[0] == 2:
        next = "3 where next=2"
    elif next_edge[0] == 3:
        next = "1 where next=3"
    sql = "UPDATE next SET " + next
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()

    img = '<img src="data:image/png;base64,' + response.json()['data'] + '"/>'
    #time = response.json()['time']
    # return str(time)
    return img


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

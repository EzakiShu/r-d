import tensorflow as tf
from flask import Flask, request, jsonify, abort
from keras.preprocessing import image
import numpy as np
from keras.models import load_model
import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image, ImageOps
from converter import i2b, b2i
from io import BytesIO
import time
import requests
import mysql.connector

app = Flask(__name__)


graph = tf.get_default_graph()


def detect_img(yolo, image):
    r_image = yolo.detect_image(image)
    return r_image


FLAGS = None


@app.route('/')
def hello():
    return "Connect"


@app.route('/api/predict', methods=["POST"])
def predict():
    # 実行時間計測
    #start = time.time()

    # database接続
    conn = mysql.connector.connect(
        host='mysql-server',
        port='3306',
        user='devuser',
        password='devuser',
        database='time'
    )
    cursor = conn.cursor(buffered=True)
    sql = ("SELECT pod FROM depth WHERE time=(SELECT MIN(time) FROM depth)")
    cursor.execute(sql)
    min_time_edge = cursor.fetchone()

    global graph
    with graph.as_default():
        # POSTされたファイルをOpenCVに変換
        image_data = b2i(request.form['data'])

        # OpenCV -> Pillow
        image = Image.fromarray(image_data)

        global model
        re_image = detect_img(model, image)

        # Pillow -> OpenCV
        cv_image = np.array(re_image)

        # バイナリに変換
        img_b = i2b(cv_image)

        # 距離推定
        url = "http://python-" + min_time_edge[0] + ":8090/depth"
        img_data = {
            "data": request.form['data']
        }
        response = requests.post(url, data=img_data)

        # 実行時間の計算
        # end = time.time() - start

        # 画像の返信
        img_data = {
            "data1": img_b,
            "data2": response.json()['data']
            # "time": end
        }

        return jsonify(img_data)


model = None
if __name__ == "__main__":

    Namespace = type("Hoge", (object,), {
        "image": True,
        "input": './path2your_video',
        "output": ''
    })

    model = YOLO(**vars(Namespace))

    # サーバーの起動
    app.run(debug=False, host='0.0.0.0', port=8081, threaded=True)

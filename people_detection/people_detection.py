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
    start = time.time()
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

        # 画像の返信
        img_data = {
            "data": img_b
        }

        # database接続
        conn = mysql.connector.connect(
            host='mysql-server',
            port='3306',
            user='devuser',
            password='devuser',
            database='time'
        )

        # 実行時間の計算
        end = time.time() - start
        cursor = conn.cursor()
        sql = "UPDATE detection SET time=15 WHERE pod='detection1'"
        # sql = "UPDATE detection SET time=" + \
        #   str(end) + " WHERE pod='detection1'"
        cursor.execute(sql)
        cursor.close()
        conn.close()

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

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
import cv2
import json

app = Flask(__name__)

import tensorflow as tf
graph = tf.get_default_graph()

def detect_img(yolo, image):
      r_image = yolo.detect_image(image)
      return r_image

FLAGS = None

# /api/predict にPOSTリクエストされたら予測値を返す関数
@app.route('/api/predict', methods=["POST"])
def predict():
    global graph
    with graph.as_default():
        #POSTされたファイルをOpenCVに変換
        image_data = b2i(request.form['data'])
        
        #OpenCV -> Pillow
        image = Image.fromarray(image_data)
        
        global model
        re_image = detect_img(model, image)

        #Pillow -> OpenCV
        cv_image = np.array(re_image)
        
        #バイナリに変換
        img_b = i2b(cv_image)

        #画像の返信
        img_data = {
            "data":img_b
        }
        return jsonify(img_data)

@app.route('/hello', methods=["POST"])
def Hello():
    return "Connect"

model = None
if __name__ == "__main__":

    Namespace = type("Hoge",(object,),{
    "image" : True,
    "input" : './path2your_video',
    "output" : ''
    })

    model = YOLO(**vars(Namespace))

    # サーバーの起動
    app.run(debug=False, host='0.0.0.0', port=8081)

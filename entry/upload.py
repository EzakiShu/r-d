import os, json, sys, requests, cv2
import numpy as np
from flask import Flask, request, redirect, url_for,jsonify
from flask import send_from_directory, render_template
from werkzeug.utils import secure_filename
import random, string, datetime
from converter import i2b, b2i

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def uploads_file():
    #opencvでPOSTされたファイルを読み込む
    file_data = request.files['file'].read()
    nparr = np.fromstring(file_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #バイナリに変換
    img_b = i2b(img)

    #画像の送信
    url = "http://python-detection1:8080/api/predict"
    img_data = {
        "data":img_b
    }
    response = requests.post(url,data=img_data)
    #return jsonify(response.json())
    img = '<img src="data:image/png;base64,' + response.json()['data'] + '"/>'
    return img

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080,threaded=True)
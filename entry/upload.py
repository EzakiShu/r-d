import requests
import cv2
import numpy as np
from flask import Flask, request
from flask import render_template
from werkzeug.utils import secure_filename
from converter import i2b, b2i

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

    # 時間を取得
    url = "http://time-data:10000/get-time"
    time_data = requests.post(url, data=0)
    time_data = {
        "detection1": float(time_data.json()["detection1"]),
        "detection2": float(time_data.json()["detection2"]),
        "detection3": float(time_data.json()["detection3"])
    }

    # 直前の実行時間が最短なPod
    min_time_edge = min(time_data.items(), key=lambda x: x[1])[0]

    # 画像の送信
    url = "http://python-" + min_time_edge + ":8080/api/predict"
    img_data = {
        "data": img_b
    }
    response = requests.post(url, data=img_data)

    img = '<img src="data:image/png;base64,' + response.json()['data'] + '"/>'
    #time = response.json()['time']
    # return str(time)
    return img


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

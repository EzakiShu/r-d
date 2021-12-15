import requests
import cv2
import numpy as np
import mysql.connector
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

    # database接続
    conn = mysql.connector.connect(
        host='mysql-server',
        port='3306',
        user='devuser',
        password='devuser',
        database='time'
    )
    cursor = conn.cursor()
    sql = ("SELECT pod FROM detection WHERE time=(SELECT MIN(time) FROM detection)")
    cursor.execute(sql)
    min_time_edge = cursor.fetchall()

    cursor.close()
    conn.close()

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

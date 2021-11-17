from flask import Flask, request, jsonify, abort, render_template
import numpy as np
import sys
from PIL import Image, ImageOps
from converter import i2b, b2i
from io import BytesIO
import cv2
import json
import tensorflow as tf
from test_split import load_model, est_image

app     = Flask(__name__)
device  = None
feed    = []
encoder = None
depth_decoder = None

@app.route('/')
def index():
  return "Hello World!"

@app.route('/depth')
def upload():
  return render_template('upload.html') 

@app.route('/depth', methods=["POST"])
def estimate():
  # POSTされたファイルをOpenCVに変換
  file_data = request.files['file'].read()
  image_np = np.fromstring(file_data, np.uint8)
  image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
  
  # OpenCV -> Pillow
  image_pil = Image.fromarray(image)
  
  # depth estimate
  global device, feed, encoder, depth_decoder
  depth_image_pil = est_image(image_pil, device, feed, encoder, depth_decoder)

  # Pillow -> OpenCV
  depth_image_bgr = np.array(depth_image_pil)
  depth_image = cv2.cvtColor(depth_image_bgr, cv2.COLOR_BGR2RGB) 
  
  # バイナリに変換
  image_b = i2b(depth_image)

  return render_template('upload.html', image=image_b)
        
if __name__ == "__main__":
  
  art_args = type("hoge", (object,), {
    "ext"               : "jpg",
    "image_path"        : "",
    "model_name"        : "mono_1024x320",
    "no_cuda"           : False,
    "pred_metric_depth" : False
  })

  # モデルの読み込み 
  device, feed, encoder, depth_decoder = load_model(art_args)
  
  # サーバーの起動
  app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

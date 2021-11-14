import cv2
import numpy as np
from PIL import Image
import base64
import io

def i2b(img_a):
  _, encimg = cv2.imencode(".png", img_a)
  img_str = encimg.tostring()
  img_b = base64.b64encode(img_str).decode("utf-8")
  return img_b

def b2i(img_b):
  decimg = base64.b64decode(img_b)
  data_np = np.fromstring(decimg, dtype='uint8')
  img_a = cv2.imdecode(data_np, flags=cv2.IMREAD_COLOR) 
  return img_a

def b2g(img_b):
  decimg = base64.b64decode(img_b)
  data_np = np.fromstring(decimg, dtype='uint8')
  img_a = cv2.imdecode(data_np, flags=cv2.IMREAD_GRAYSCALE) 
  return img_a
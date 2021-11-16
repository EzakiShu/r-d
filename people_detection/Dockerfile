FROM python:3.6
EXPOSE 5000
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/people_detection
RUN python -m pip install --upgrade pip
RUN pip install Flask
RUN pip install opencv-python
RUN pip install tensorflow==1.13.1
RUN pip install keras==2.2.2
RUN pip install numpy
RUN pip install scipy
RUN pip install pillow
RUN pip uninstall h5py
RUN pip install h5py==2.10.0
RUN wget git clone https://github.com/qqwweee/keras-yolo3
WORKDIR /keras-yolo3
RUN python convert.py yolov3.cfg yolov3.weights model_data/yolo.h5
ENTRYPOINT python people_detection.py

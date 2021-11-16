FROM python:3.6
EXPOSE 5000
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/people_detection
RUN export workdir='pwd'
RUN python -m pip install --upgrade pip
RUN pip install Flask
RUN pip install h5py==2.10.0
RUN pip install opencv-python
RUN pip install tensorflow==1.13.1
RUN pip install keras==2.2.2
RUN pip install numpy
RUN pip install scipy
RUN pip install pillow
RUN git clone https://github.com/qqwweee/keras-yolo3
WORKDIR keras-yolo3
RUN wget https://pjreddie.com/media/files/yolov3.weights
RUN python convert.py yolov3.cfg yolov3.weights model_data/yolo.h5
RUN cp $workdir/converter.py $workdir/people_detection.py $workdir/yolo.py
ENTRYPOINT python people_detection.py

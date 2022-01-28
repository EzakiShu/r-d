FROM python:3.6
ARG BRANCH="main"
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/hoge
RUN git checkout origin/$BRANCH
RUN python -m pip install --upgrade pip
RUN apt update
RUN pip install Flask
RUN pip install opencv-python
RUN pip install numpy
RUN pip install requests
RUN pip install pillow
RUN apt install -y libgl1-mesa-dev
RUN pip install mysql-connector-python
ENTRYPOINT python upload.py


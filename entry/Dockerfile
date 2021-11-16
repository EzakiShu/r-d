FROM python:3.6
EXPOSE 5000
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/entry
RUN python -m pip install --upgrade pip
RUN apt update
RUN pip install Flask
RUN pip install opencv-python
RUN pip install numpy
RUN pip install requests
RUN apt install -y libgl1-mesa-dev
ENTRYPOINT python upload.py


FROM python:3.6
ARG BRANCH=main
WORKDIR /app
RUN apt update
RUN apt install -y libgl1-mesa-dev
RUN python -m pip install --upgrade pip
RUN pip install Flask opencv-python numpy pillow matplotlib requests
RUN pip install torch
RUN git clone https://github.com/nianticlabs/monodepth2.git
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/
RUN git checkout origin/$BRANCH
RUN cp -r depth-estimate/* ../monodepth2
WORKDIR /app/monodepth2
ENTRYPOINT python depth-estimate.py


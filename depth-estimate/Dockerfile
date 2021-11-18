FROM python:3.6
ARG BRANCH=main
WORKDIR /app
RUN apt update
RUN apt install -y libgl1-mesa-dev unzip
RUN python -m pip install --upgrade pip
RUN pip install Flask opencv-python numpy pillow matplotlib requests
RUN pip install torch torchvision  scikit-image
RUN git clone https://github.com/nianticlabs/monodepth2.git
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/
RUN git checkout origin/$BRANCH
RUN cp -r depth-estimate/* ../monodepth2
WORKDIR /app/monodepth2/models
RUN wget https://storage.googleapis.com/niantic-lon-static/research/monodepth2/mono_1024x320.zip
RUN unzip mono_1024x320.zip
WORKDIR /app/monodepth2
ENTRYPOINT python depth-estimate.py


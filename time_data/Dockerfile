FROM python:3.6
ARG BRANCH="main"
RUN git clone https://github.com/EzakiShu/r-d.git
WORKDIR r-d/time_data
RUN git checkout origin/$BRANCH
RUN python -m pip install --upgrade pip
RUN apt update
RUN pip install Flask
ENTRYPOINT python time_data.py


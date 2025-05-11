FROM python:3.13-slim-bookworm AS pic_orientation

ENV APPNAME=picrobo
ENV HOME_FOLDER=/$APPNAME
ENV TZ="Europe/Berlin"
WORKDIR $HOME_FOLDER

COPY requirements.txt /tmp/pip-tmp/requirements.txt

RUN apt -y update
RUN apt -y upgrade
RUN apt install -y git build-essential cmake && pip install --upgrade pip 
RUN pip install -r /tmp/pip-tmp/requirements.txt && rm -rf /tmp/pip-tmp

#RUN apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN apt install -y ffmpeg libsm6 libxext6
COPY *   $HOME_FOLDER/

CMD ["bash"]
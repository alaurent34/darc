FROM ubuntu:latest

RUN apt-get update --fix-missing
RUN apt-get install -y python3.6 python3-distutils build-essential python3.6-dev curl
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

# Fixes error when installing pyocclient
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 229: ordinal not in range(128)
RUN apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
ENV PYTHONIOENCODING=utf-8

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY requirements.txt /requirements.txt

RUN pip3.6 install -r /requirements.txt

ADD . /DARC

WORKDIR /DARC

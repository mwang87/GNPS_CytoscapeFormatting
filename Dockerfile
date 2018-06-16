FROM ubuntu:latest
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y libxml2-dev

RUN pip install ftputil
RUN pip install flask
RUN pip install gunicorn
RUN pip install requests
RUN pip install py2cytoscape


COPY . /app
WORKDIR /app

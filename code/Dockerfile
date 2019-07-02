FROM ubuntu:latest
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y zlib1g-dev
RUN apt-get install -y libxml2-dev
RUN apt-get install -y xvfb

RUN pip3 install ftputil
RUN pip3 install flask
RUN pip3 install gunicorn
RUN pip3 install requests
RUN pip3 install py2cytoscape

RUN apt-get install -y openjdk-8-jre
RUN apt-get install -y wget

RUN wget http://chianti.ucsd.edu/cytoscape-3.6.1/Cytoscape_3_6_1_unix.sh
RUN chmod u+x  Cytoscape_3_6_1_unix.sh
RUN sh Cytoscape_3_6_1_unix.sh -q

RUN pip3 install pathvalidate
RUN pip3 install psutil
RUN pip3 install redis
RUN pip3 install -U Celery

COPY . /app
WORKDIR /app

CMD ["sh", "/app/run_server_in_docker.sh"]
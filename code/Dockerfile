FROM ubuntu:20.04
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential zlib1g-dev libxml2-dev xvfb wget
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y tzdata
RUN apt-get update && apt-get install -y python3-pip python3-dev openjdk-8-jre

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get install -y ttf-dejavu fontconfig

RUN wget http://chianti.ucsd.edu/cytoscape-3.6.1/Cytoscape_3_6_1_unix.sh
RUN chmod u+x  Cytoscape_3_6_1_unix.sh
RUN sh Cytoscape_3_6_1_unix.sh -q

# Setting the options properly
RUN echo "-Xms2048M\n-Xmx8096M" > /usr/local/Cytoscape_v3.6.1/Cytoscape.vmoptions

COPY . /app
COPY ./run_server.sh /app/run_server.sh
WORKDIR /app
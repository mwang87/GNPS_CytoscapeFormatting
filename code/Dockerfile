FROM continuumio/miniconda3:4.10.3
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && apt-get install -y build-essential zlib1g-dev libxml2-dev tzdata xvfb wget

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN conda install -c conda-forge mamba
RUN mamba install -c conda-forge openjdk=9 -y

RUN wget http://chianti.ucsd.edu/cytoscape-3.6.1/Cytoscape_3_6_1_unix.sh
RUN chmod u+x  Cytoscape_3_6_1_unix.sh
RUN sh Cytoscape_3_6_1_unix.sh -q

# Setting the options properly
RUN echo "-Xms2048M\n-Xmx8096M" > /usr/local/Cytoscape_v3.6.1/Cytoscape.vmoptions

COPY . /app
WORKDIR /app

CMD ["sh", "/app/run_server_in_docker.sh"]
FROM ubuntu:20.04
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential zlib1g-dev libxml2-dev xvfb wget
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y tzdata
RUN apt-get update && apt-get install -y python3-pip python3-dev openjdk-8-jre

# Install Conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_22.11.1-1-Linux-x86_64.sh && bash Miniconda3-py37_22.11.1-1-Linux-x86_64.sh -b


#RUN conda install -c conda-forge mamba
#RUN mamba create -n cytoscape python=3.7
#RUN mamba install -n cytoscape -c conda-forge openjdk=8 -y

COPY requirements.txt .
#RUN /bin/bash -c 'source activate cytoscape && pip install -r requirements.txt'
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

# FROM ubuntu:20.04
# MAINTAINER Mingxun Wang "mwang87@gmail.com"

# RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential zlib1g-dev libxml2-dev xvfb wget
# RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y tzdata libarchive-dev wget vim ttf-dejavu fontconfig

# # Install Mamba
# ENV CONDA_DIR /opt/conda
# RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O ~/miniforge.sh && /bin/bash ~/miniforge.sh -b -p /opt/conda
# ENV PATH=$CONDA_DIR/bin:$PATH

# # Adding to bashrc
# RUN echo "export PATH=$CONDA_DIR:$PATH" >> ~/.bashrc

# # Installing everything for cytoscape
# RUN mamba create -n cytoscape python=3.7
# RUN mamba install -n cytoscape -c conda-forge openjdk=8 -y
# COPY requirements.txt .
# RUN /bin/bash -c 'source activate cytoscape && pip install -r requirements.txt'
# RUN pip install -r requirements.txt

# RUN wget http://chianti.ucsd.edu/cytoscape-3.6.1/Cytoscape_3_6_1_unix.sh
# RUN chmod u+x  Cytoscape_3_6_1_unix.sh
# RUN sh Cytoscape_3_6_1_unix.sh -q

# # Setting the options properly
# RUN echo "-Xms2048M\n-Xmx8096M" > /usr/local/Cytoscape_v3.6.1/Cytoscape.vmoptions

# COPY . /app
# COPY ./run_server.sh /app/run_server.sh
# WORKDIR /app
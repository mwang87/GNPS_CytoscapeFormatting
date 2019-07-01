#!/bin/bash

#Running Cytoscape Virtual Buffer
Xvfb :1 &
export DISPLAY=:1
#Cytoscape &

#Running Celery Worker
sh ./run_celery_worker.sh &

#Running Web Server

#Dev Version
python3 ./main.py

#Production Version
#gunicorn -w 8 -b 0.0.0.0:5051 --timeout 3600 main:app

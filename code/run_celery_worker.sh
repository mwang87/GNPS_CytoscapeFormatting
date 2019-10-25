#!/bin/bash

#Trying to remove X1 lock
rm /tmp/.X1-lock || true

#Running Cytoscape Virtual Buffer
Xvfb :1 &
sleep 1
export DISPLAY=:1

celery -A cytoscape_tasks worker -l info -c 1
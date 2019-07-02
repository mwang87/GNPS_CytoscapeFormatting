#!/bin/bash

#Running Cytoscape Virtual Buffer
Xvfb :1 &
export DISPLAY=:1

celery -A cytoscape_tasks worker -l info -c 1
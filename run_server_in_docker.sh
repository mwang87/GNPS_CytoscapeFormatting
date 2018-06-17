#!/bin/bash

Xvfb :1 &
export DISPLAY=:1
Cytoscape &
python3 ./main.py

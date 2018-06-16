# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from py2cytoscape.data.cyrest_client import CyRestClient

from app import app
from werkzeug.utils import secure_filename
import os
import glob
import json
import requests
from time import sleep

@app.route('/', methods=['GET'])
def homepage():
    return render_template("homepage.html")

@app.route('/process', methods=['GET'])
def process():
    taskid = request.args["task"]

    return render_template("process.html", task=taskid)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    taskid = request.args["task"]
    return render_template("dashboard.html", task=taskid)

@app.route('/process', methods=['POST'])
def process_ajax():
    print(request.args)
    taskid = request.args["task"]

    path_to_graphml = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)

    local_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "%s.graphml" % (taskid))
    local_file = open(local_filepath, "w")
    local_file.write(requests.get(path_to_graphml).text)
    local_file.close()

    clean_gc_url = "http://localhost:1234/v1/gc"
    requests.get(clean_gc_url)

    cy  = CyRestClient()
    cy.session.delete()
    #network1 = cy.network.create_from("/home/mingxun/Downloads/METABOLOMICS-SNETS-V2-305674ff-download_cytoscape_data-main.graphml")
    network1 = cy.network.create_from(local_filepath)

    mystyle = cy.style.create("Sample2")

    new_defaults = {
        # Node defaults
        'NODE_CUSTOMGRAPHICS_1': 'org.cytoscape.PieChart:{"cy_range":[0.0,0.0],"cy_colors":["#FF0000","#8000FF","#00FFFF","#80FF00"],"cy_dataColumns":["G1","G2","G3","G4"]}'
    }
    mystyle.create_passthrough_mapping(column='Compound_Name', col_type='String', vp='NODE_LABEL')
    mystyle.update_defaults(new_defaults)

# TO update, change the style in real cytoscape, and look for string here: http://localhost:1234/v1/styles/Ming2

    cy.style.apply(style=mystyle, network=network1)

    sleep(2)

    local_cytoscape_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.cys" % (taskid)))
    cy.session.save(local_cytoscape_file)

    cy.layout.fit(network=network1)

    sleep(2)

    local_png_file = open(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.png" % (taskid))), "wb")
    local_png_file.write(network1.get_png())
    local_png_file.close()

    clean_gc_url = "http://localhost:1234/v1/gc"
    requests.get(clean_gc_url)

    return "{}"

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

    cy  = CyRestClient()
    cy.session.delete()
    #network1 = cy.network.create_from("/home/mingxun/Downloads/METABOLOMICS-SNETS-V2-305674ff-download_cytoscape_data-main.graphml")
    network1 = cy.network.create_from(local_filepath)

    mystyle = cy.style.create("Sample2")
    cy.style.apply(style=mystyle, network=network1)

    sleep(2)

    local_cytoscape_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.cys" % (taskid)))
    cy.session.save(local_cytoscape_file)

    cy.layout.fit(network=network1)

    sleep(2)

    local_png_file = open(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.png" % (taskid))), "wb")
    local_png_file.write(network1.get_png())
    local_png_file.close()

    return "{}"

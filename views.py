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
import subprocess
from time import sleep
import random
import metabotracker

@app.route('/', methods=['GET'])
def homepage():
    return render_template("homepage.html")

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/process', methods=['GET'])
def process():
    taskid = request.args["task"]

    return render_template("process.html", task=taskid)

@app.route('/metabotracker', methods=['GET'])
def metabotracker_view():
    taskid = request.args["task"]
    source = request.args["source"]

    return render_template("metabotracker.html", task=taskid, source=source)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    taskid = request.args["task"]
    return render_template("dashboard.html", task=taskid, randomnumber=str(random.randint(1,10001)))

def get_graph_object(taskid):
    task_status_url = "https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task=%s" % (taskid)

    task_status = requests.get(task_status_url).json()
    url_to_graph = ""

    if task_status["workflow"] == "NAP_CCMS2":
        url_to_graph = "https://proteomics2.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=final_out/structure_graph_alt.xgmml" % (taskid)
    if task_status["workflow"] == "METABOLOMICS-SNETS-V2":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
    if task_status["workflow"] == "METABOLOMICS-SNETS":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
    if task_status["workflow"] == "METABOLOMICS-SNETS-MZMINE":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
    if task_status["workflow"] == "FEATURE-BASED-MOLECULAR-NETWORKING":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
    if task_status["workflow"] == "MS2LDA_MOTIFDB":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=output_graphml/ms2lda_network.graphml" % (taskid)
    if task_status["workflow"] == "MOLNETENHANCER":
        url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=output_network/ClassyFireResults_Network.graphml" % (taskid)


    print(url_to_graph)

    local_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "%s.graphml" % (taskid))
    local_file = open(local_filepath, "w")
    local_file.write(requests.get(url_to_graph).text)
    local_file.close()

    return local_filepath

@app.route('/process', methods=['POST'])
def process_ajax():
    print(request.args)
    #PORT_NUMBER = 1234

    taskid = request.args["task"]
    local_filepath = get_graph_object(taskid)

    if "metabotracker" in request.args:
        source = request.args["metabotracker"]
        metabotracker.metabotracker_wrapper(local_filepath, local_filepath, source=source)

    cytoscape_process = subprocess.Popen("Cytoscape", shell=True)

    #Check if server is up
    while(1):
        try:
            cy  = CyRestClient()
            #new_cy = cyrest(port=PORT_NUMBER)
            break
        except:
            print("Failed Cyrest")
            sleep(1)
            continue

    cy  = CyRestClient()
    network1 = cy.network.create_from(local_filepath)

    mystyle = cy.style.create("ClassDefault")

    #Loading style
    all_parameters = json.loads(open("Styles/Sample2.json").read())


    new_defaults_dict = {}
    for item in all_parameters["defaults"]:
        new_defaults_dict[item["visualProperty"]] = item["value"]

    mappings_list = all_parameters["mappings"]
    for mapping in mappings_list:
        if mapping["mappingType"] == "passthrough":
            mystyle.create_passthrough_mapping(column=mapping["mappingColumn"], col_type=mapping["mappingColumnType"], vp=mapping["visualProperty"])

    mystyle.update_defaults(new_defaults_dict)

    #new_defaults = {
    #    # Node defaults
    #    'NODE_CUSTOMGRAPHICS_1': 'org.cytoscape.PieChart:{"cy_range":[0.0,0.0],"cy_colors":["#FF0000","#8000FF","#00FFFF","#80FF00"],"cy_dataColumns":["G1","G2","G3","G4"]}'
    #}
    #mystyle.create_passthrough_mapping(column='Compound_Name', col_type='String', vp='NODE_LABEL')

# TO update, change the style in real cytoscape, and look for string here: http://localhost:1234/v1/styles/Ming2

    cy.style.apply(style=mystyle, network=network1)

    sleep(1)

    local_cytoscape_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.cys" % (taskid)))
    cy.session.save(local_cytoscape_file)

    cy.layout.fit(network=network1)
    #print(cy.__dict__)
    #cy.view.fit_content()

    sleep(1)

    local_png_file = open(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.png" % (taskid))), "wb")
    local_png_file.write(network1.get_png())
    local_png_file.close()

    #clean_gc_url = "http://localhost:1234/v1/gc"
    #requests.get(clean_gc_url)
    requests.get("http://localhost:%d/v1/commands/command/quit" % (1234))
    #cy.command.quit()

    return "{}"

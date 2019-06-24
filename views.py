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

    query_parameters = {"task" : taskid}

    return render_template("process.html", task=taskid, query_parameters=query_parameters)

@app.route('/metabotracker', methods=['GET'])
def metabotracker_view():
    taskid = request.args["task"]
    source = request.args["source"]

    query_parameters = {"task" : taskid, "filter": "tagtracker", "source": source}

    return render_template("process.html", task=taskid, query_parameters=query_parameters)

@app.route('/molnetenhancer', methods=['GET'])
def molnetenhancer_view():
    taskid = request.args["task"]
    molnetenhancer_class = request.args["molnetenhancer_class"]

    query_parameters = {"task" : taskid, "filter": "molnetenhancer", "molnetenhancer_class": molnetenhancer_class}

    return render_template("process.html", task=taskid, query_parameters=query_parameters)

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

    return local_filepath, task_status["workflow"]


@app.route('/process', methods=['POST'])
def process_ajax():
    print(request.values)

    style_filename = "Styles/Sample2.json"
    taskid = request.values["task"]
    local_filepath, workflow_name = get_graph_object(taskid)

    #Defining style given the type of data
    if workflow_name == "MOLNETENHANCER":
        style_filename = "Styles/MolnetEnhancer_ChemicalSuperClasses.json"

    if "filter" in request.values:
        if request.values["filter"] == "tagtracker":
            print("Tag Tracker")
            source = request.values["source"]
            sources_list = [source]
            metabotracker.metabotracker_wrapper(local_filepath, local_filepath, source=sources_list)
        if request.values["filter"] == "molnetenhancer":
            print("Molnetenhancer")
            metabotracker.molnetenhancer_wrapper(local_filepath, local_filepath, class_header="CF_class", class_name=request.values["molnetenhancer_class"])
            style_filename = "Styles/MolnetEnhancer_ChemicalSuperClasses.json"

    cytoscape_process = subprocess.Popen("Cytoscape", shell=True)

    #Check if server is up
    while(1):
        try:
            cy  = CyRestClient()
            print("Success Cyrest")
            #new_cy = cyrest(port=PORT_NUMBER)
            break
        except:
            print("Failed Cyrest")
            sleep(1)
            continue

    cy  = CyRestClient()
    network1 = cy.network.create_from(local_filepath)

    mystyle = cy.style.create("ClassDefault")

    """Loading style"""
    all_parameters = json.loads(open(style_filename).read())

    new_defaults_dict = {}
    for item in all_parameters["defaults"]:
        new_defaults_dict[item["visualProperty"]] = item["value"]

    #Loading the passthrough mapping
    mappings_list = all_parameters["mappings"]
    for mapping in mappings_list:
        if mapping["mappingType"] == "passthrough":
            mystyle.create_passthrough_mapping(column=mapping["mappingColumn"], col_type=mapping["mappingColumnType"], vp=mapping["visualProperty"])

    #Loading the descrete mapping
    for mapping in mappings_list:
        if mapping["mappingType"] == "discrete":
            reformatted_mapping = {}
            for item in mapping["map"]:
                reformatted_mapping[item["key"]] = item["value"]
            mystyle.create_discrete_mapping(column=mapping["mappingColumn"], col_type=mapping["mappingColumnType"],
                                vp=mapping["visualProperty"], mappings=reformatted_mapping)

    #Loading a continuous mapping, TODO: need to debug
    for mapping in mappings_list:
        if mapping["mappingType"] == "continuous":
            mystyle.create_continuous_mapping(column=mapping["mappingColumn"], col_type=mapping["mappingColumnType"],
                                  vp=mapping["visualProperty"], points=mapping["points"])


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

# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from py2cytoscape.data.cyrest_client import CyRestClient

from app import app
#from app import celery_instance
from cytoscape_tasks import test_celery

from werkzeug.utils import secure_filename
import os
import glob
import json
import requests
import subprocess
from time import sleep
import random
import shutil
import urllib
import metabotracker
from pathvalidate import sanitize_filename


@app.route('/', methods=['GET'])
def homepage():
    return render_template("homepage.html")

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/process', methods=['GET'])
def process():
    taskid = request.args["task"]

    return render_template("process.html", task=taskid, query_parameters=dict(request.values))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)

    return render_template("dashboard.html", \
        cytoscapefilename=os.path.basename(output_cytoscape_filename), \
        imagefilename=os.path.basename(output_img_filename), \
        randomnumber=str(random.randint(1,10001)))

#Retreiving graphml from workflow output. 
def get_graph_object(taskid):
    task_status_url = "https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task=%s" % (taskid)

    task_status = requests.get(task_status_url).json()
    url_to_graph = ""

    local_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "%s.graphml" % (taskid))

    if task_status["workflow"] == "MS2LDA_MOTIFDB":
        #Special case using zip file
        url_to_zip = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task=%s&show=true&view=download_cytoscape_data" % (taskid)
        r = requests.post(url_to_zip)

        zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], "%s.zip" % (taskid))
        local_file = open(zip_filename, "wb")
        local_file.write(r.content)
        local_file.close()

        from zipfile import ZipFile
        with ZipFile(zip_filename, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            for fileName in listOfFileNames:
                if fileName.endswith('.graphml'):
                    source = zipObj.open(fileName)
                    target = open(os.path.join(app.config['UPLOAD_FOLDER'], "%s.graphml" % (taskid)), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                    #Found, lets break
                    break

    else:
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
        if task_status["workflow"] == "MOLNETENHANCER":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=output_network/ClassyFireResults_Network.graphml" % (taskid)

        print(url_to_graph)
        local_file = open(local_filepath, "w")
        local_file.write(requests.get(url_to_graph).text)
        local_file.close()

    return local_filepath, task_status["workflow"]

@app.route('/testcelery', methods=['GET'])
def test_celery_endpoint():
    #Putting the request on the queue
    style_filename = ""
    local_filepath = ""

    print("Before Celery Submit")
    result = test_celery.delay(4)
    print(result)
    print("After Celery Submit")
    result.ready()
    result = result.get()

    return str(result)

#Actually doing the processing
@app.route('/process', methods=['POST'])
def process_ajax():
    print(request.values)

    output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)
    
    if os.path.exists(output_cytoscape_filename):
        return json.dumps({"redirect_url" : "/dashboard?%s" % (urllib.parse.urlencode(request.values))})

    print(output_cytoscape_filename, output_img_filename)

    style_filename = "Styles/Sample2.json"
    taskid = request.values["task"]
    local_filepath, workflow_name = get_graph_object(taskid)

    #Defining style given the type of data
    if workflow_name == "MOLNETENHANCER":
        style_filename = "Styles/MolnetEnhancer_ChemicalSuperClasses.json"
    if workflow_name == "MS2LDA_MOTIFDB":
        style_filename = "Styles/MotifEdgesStyle.json"

    #Option to filter data
    if "filter" in request.values:
        if request.values["filter"] == "tagtracker":
            print("Tag Tracker")
            source = request.values["source"]
            sources_list = [source]
            metabotracker.metabotracker_wrapper(local_filepath, local_filepath, source=sources_list)
        if request.values["filter"] == "molnetenhancer":
            print("Molnetenhancer")
            super_classname = request.values["molnetenhancer_superclass"]
            metabotracker.molnetenhancer_wrapper(local_filepath, local_filepath, class_header="CF_superclass", class_name=super_classname)
            style_filename = "Styles/MolnetEnhancer_ChemicalClasses.json"

    #Doing it in the thread
    #create_cytoscape(local_filepath, style_filename, output_cytoscape_filename, output_img_filename)

    
    return json.dumps({"redirect_url" : "/dashboard?%s" % (urllib.parse.urlencode(request.values))})

#Test Function
def test_function(a, b, c, d):
    print(a, b, c, d)

#Calculating the output cytoscape and img filename
def calculate_output_filenames(params_dict):
    expected_keys = ["task", "filter", "source", "molnetenhancer_superclass"]
    param_keys = list(params_dict.keys())
    param_keys.sort()
    all_values = [sanitize_filename(str(params_dict[key])).replace(" ", "") for key in param_keys]

    filename_base = "_".join(all_values)

    local_cytoscape_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.cys" % (filename_base)))
    local_network_img_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.png" % (filename_base)))

    return local_cytoscape_file, local_network_img_path

#Launching Import into Cytoscape
def create_cytoscape(input_graphml, input_style, output_cytoscape_filename, output_img_filename):
    cytoscape_process = subprocess.Popen("Cytoscape", shell=True)

    cy = None
    #Check if server is up
    while(1):
        try:
            cy  = CyRestClient()
            print("Success Cyrest")
            break
        except:
            print("Failed Cyrest")
            sleep(1)
            continue

    print("Loading graphml into Cytoscape")
    network1 = cy.network.create_from(input_graphml)

    mystyle = cy.style.create("ClassDefault")

    """Loading style"""
    print("Loading Style")
    all_parameters = json.loads(open(input_style).read())

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

    # TO update, change the style in real cytoscape, and look for string here: http://localhost:1234/v1/styles/Ming2

    cy.style.apply(style=mystyle, network=network1)

    sleep(1)

    cy.session.save(output_cytoscape_filename)
    cy.layout.fit(network=network1)

    sleep(1)

    local_png_file = open(os.path.abspath(output_img_filename), "wb")
    local_png_file.write(network1.get_png())
    local_png_file.close()

    requests.get("http://localhost:%d/v1/commands/command/quit" % (1234))

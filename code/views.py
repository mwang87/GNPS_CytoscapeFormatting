# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from app import app
#from app import celery_instance
from cytoscape_tasks import test_celery
from cytoscape_tasks import create_cytoscape

from werkzeug.utils import secure_filename
import os
import glob
import json
import requests
import random
import shutil
import urllib
from time import sleep
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

    expected_graphml_filename, output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)

    if os.path.exists(output_cytoscape_filename):
        return render_template("dashboard.html", \
            cytoscapefilename=os.path.basename(output_cytoscape_filename), \
            imagefilename=os.path.basename(output_img_filename), \
            randomnumber=str(random.randint(1,10001)))

    return render_template("process.html", task=taskid, query_parameters=dict(request.values))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    expected_graphml_filename, output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)

    return render_template("dashboard.html", \
        cytoscapefilename=os.path.basename(output_cytoscape_filename), \
        imagefilename=os.path.basename(output_img_filename), \
        randomnumber=str(random.randint(1,10001)))

#Retreiving graphml from workflow output. 
def get_graph_object(taskid, workflow_name, output_graphml_filename):
    url_to_graph = ""

    if workflow_name == "MS2LDA_MOTIFDB":
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
                    target = open(output_graphml_filename, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                    #Found, lets break
                    break

    else:
        if workflow_name == "NAP_CCMS2":
            url_to_graph = "https://proteomics2.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=final_out/structure_graph_alt.xgmml" % (taskid)
        if workflow_name == "METABOLOMICS-SNETS-V2":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
        if workflow_name == "METABOLOMICS-SNETS":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
        if workflow_name == "METABOLOMICS-SNETS-MZMINE":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
        if workflow_name == "FEATURE-BASED-MOLECULAR-NETWORKING":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=gnps_molecular_network_graphml/" % (taskid)
        if workflow_name == "MOLNETENHANCER":
            url_to_graph = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=output_network/ClassyFireResults_Network.graphml" % (taskid)

        print(url_to_graph)
        local_file = open(output_graphml_filename, "w")
        local_file.write(requests.get(url_to_graph).text)
        local_file.close()

    #TODO checkout to make sure the graphml is ok
    return True

# @app.route('/testcelery', methods=['GET'])
# def test_celery_endpoint():
#     #Putting the request on the queue
#     style_filename = ""
#     local_filepath = ""

#     print("Before Celery Submit")
#     result = test_celery.delay(4, 9)
#     print(result)
#     print("After Celery Submit")
#     while(1):
#         if result.ready():
#             break
#         sleep(10)
#     result = result.get()

#     return str(result)

# @app.route('/process2', methods=['GET'])
# def process_ajax2():
#     print(request.values)

#     expected_graphml_filename, output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)
    
#     #if os.path.exists(output_cytoscape_filename):
#     #    return json.dumps({"redirect_url" : "/dashboard?%s" % (urllib.parse.urlencode(request.values))})

#     print(output_cytoscape_filename, output_img_filename)

#     style_filename = "Styles/Sample2.json"
#     taskid = request.values["task"]

#     #TESTING
#     local_filepath = expected_graphml_filename
#     workflow_name = ""
    
#     #local_filepath, workflow_name = get_graph_object(taskid)

#     #Defining style given the type of data
#     if workflow_name == "MOLNETENHANCER":
#         style_filename = "Styles/MolnetEnhancer_ChemicalSuperClasses.json"
#     if workflow_name == "MS2LDA_MOTIFDB":
#         style_filename = "Styles/MotifEdgesStyle.json"

#     #Option to filter data
#     if "filter" in request.values:
#         if request.values["filter"] == "tagtracker":
#             print("Tag Tracker")
#             source = request.values["source"]
#             sources_list = [source]
#             metabotracker.metabotracker_wrapper(local_filepath, local_filepath, source=sources_list)
#         if request.values["filter"] == "molnetenhancer":
#             print("Molnetenhancer")
#             super_classname = request.values["molnetenhancer_superclass"]
#             metabotracker.molnetenhancer_wrapper(local_filepath, local_filepath, class_header="CF_superclass", class_name=super_classname)
#             style_filename = "Styles/MolnetEnhancer_ChemicalClasses.json"

#     #Doing it in the worker
#     result = create_cytoscape.delay(local_filepath, style_filename, output_cytoscape_filename, output_img_filename)
#     print(result)
#     print("After Celery Submit")
#     while(1):
#         if result.ready():
#             break
#         sleep(10)
#     result = result.get()

#     return json.dumps({"redirect_url" : "/dashboard?%s" % (urllib.parse.urlencode(request.values))})



#Actually doing the processing
@app.route('/process', methods=['POST'])
def process_ajax():
    print(request.values)

    output_graphml_filename, output_cytoscape_filename, output_img_filename = calculate_output_filenames(request.values)
    
    # if os.path.exists(output_cytoscape_filename):
    #     return json.dumps({"redirect_url" : "/dashboard?%s" % (urllib.parse.urlencode(request.values))})

    print(output_cytoscape_filename, output_img_filename)

    style_filename = "Styles/Sample2.json"
    taskid = request.values["task"]

    task_status_url = "https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task=%s" % (taskid)
    task_status = requests.get(task_status_url).json()
    workflow_name = task_status["workflow"]

    retreval_status = get_graph_object(taskid, workflow_name, output_graphml_filename)

    if not retreval_status:
        raise Exception("Did not retreive graphml properly")

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
            metabotracker.metabotracker_wrapper(output_graphml_filename, output_graphml_filename, source=sources_list)
        if request.values["filter"] == "molnetenhancer":
            print("Molnetenhancer")
            super_classname = request.values["molnetenhancer_superclass"]
            metabotracker.molnetenhancer_wrapper(output_graphml_filename, output_graphml_filename, class_header="CF_superclass", class_name=super_classname)
            style_filename = "Styles/MolnetEnhancer_ChemicalClasses.json"

    #Doing it in the thread
    #create_cytoscape(local_filepath, style_filename, output_cytoscape_filename, output_img_filename)

    #Doing it in the worker
    result = create_cytoscape.delay(output_graphml_filename, style_filename, output_cytoscape_filename, output_img_filename)
    print(result)
    print("After Celery Submit")
    while(1):
        if result.ready():
            break
        sleep(3)
    result = result.get()

    return json.dumps({"redirect_url" : "/process?%s" % (urllib.parse.urlencode(request.values))})

#Calculating the output cytoscape and img filename
def calculate_output_filenames(params_dict):
    expected_keys = ["task", "filter", "source", "molnetenhancer_superclass"]
    param_keys = list(params_dict.keys())
    param_keys.sort()
    all_values = [sanitize_filename(str(params_dict[key])).replace(" ", "") for key in param_keys]

    filename_base = "_".join(all_values)

    local_graphml_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.graphml" % (filename_base)))
    local_cytoscape_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.cys" % (filename_base)))
    local_network_img_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], "%s.png" % (filename_base)))

    return local_graphml_file, local_cytoscape_file, local_network_img_path


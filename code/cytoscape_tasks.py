from celery import Celery
import subprocess
import requests
from time import sleep
import json
import os
import networkx as nx
import psutil

from py2cytoscape.data.cyrest_client import CyRestClient


print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='redis://cytoscape-redis', broker='redis://cytoscape-redis')

@celery_instance.task
def test_celery(input_value, input_value2):
    sleep(60)
    return input_value + input_value2

#Launching Import into Cytoscape
@celery_instance.task(time_limit=120)
def create_cytoscape(input_graphml, input_style, output_cytoscape_filename, output_img_filename, force_generate=False):
    # #Lets check if the output is already there
    if os.path.exists(output_cytoscape_filename) and force_generate == False:
        return

    #Check if the number of nodes is too large
    print("GRAPHML SIZE", input_graphml, os.path.getsize(input_graphml))

    network_graph = nx.read_graphml(input_graphml)
    number_of_nodes = network_graph.number_of_nodes()
    number_of_edges = network_graph.number_of_edges()
    print("Graph node count", number_of_nodes)
    print("Graph edge count", number_of_edges)

    # TODO: Cleanup Cytoscape Executables

    # MAX_NODES = 10000
    # MAX_EDGES = 50000
    # if number_of_nodes > MAX_NODES:
    #     raise Exception("Too Many Nodes in Graphml, will crash Cytoscape")
    # if number_of_edges > MAX_EDGES:
    #     raise Exception("Too Many EDGES in Graphml, will crash Cytoscape")

    cytoscape_process = subprocess.Popen("Cytoscape", shell=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)


    cy = None
    #Check if server is up
    while(1):
        try:
            cy = CyRestClient()
            print("Success Cyrest")
            break
        except:
            print("Failed Cyrest")
            if cytoscape_process.poll() != None:
                process_output, process_erroutput =  cytoscape_process.communicate()
                print("Error Cytoscape Died Before we could Use")
                print(process_output, process_erroutput)
            #    return
            sleep(3)
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

    # To update, change the style in real cytoscape, and look for string here: http://localhost:1234/v1/styles/Ming2

    cy.style.apply(style=mystyle, network=network1)

    sleep(1)

    cy.session.save(output_cytoscape_filename)
    cy.layout.fit(network=network1)

    sleep(1)

    local_png_file = open(os.path.abspath(output_img_filename), "wb")
    local_png_file.write(network1.get_png())
    local_png_file.close()

    #Clean up
    requests.get("http://localhost:%d/v1/commands/command/quit" % (1234))

    #TODO: Perform more compehensive cleanup
    cytoscape_process.kill()


    for proc in psutil.process_iter(attrs=['pid', 'name', 'username']):
        if "java" in proc.info["name"]:
            print("Killing Java")
            proc.kill()
        
from celery import Celery
import subprocess
import requests
from time import sleep
import json
import os

from py2cytoscape.data.cyrest_client import CyRestClient


print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='redis://redis', broker='redis://redis')

@celery_instance.task
def test_celery(input_value, input_value2):
    return input_value + input_value2

#Launching Import into Cytoscape
@celery_instance.task
def create_cytoscape(input_graphml, input_style, output_cytoscape_filename, output_img_filename):
    cytoscape_process = subprocess.Popen("Cytoscape", shell=True)

    cy = None
    #Check if server is up
    while(1):
        try:
            cy = CyRestClient()
            print("Success Cyrest")
            break
        except:
            print("Failed Cyrest")
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

    requests.get("http://localhost:%d/v1/commands/command/quit" % (1234))

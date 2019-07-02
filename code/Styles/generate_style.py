"""Lets try to get all visual properties and save to json files ourselves"""

from py2cytoscape import cyrest
import sys
import json

cytoscape=cyrest.cyclient()
cytoscape.version()
cytoscape.network.list()

full_style_json = cytoscape.styles.getStyleFull(sys.argv[1], verbose=True).json()

open(sys.argv[2], "w").write(json.dumps(full_style_json, indent=4))

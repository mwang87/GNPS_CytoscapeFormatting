"""Lets try to get all visual properties and save to json files ourselves"""

import sys
import json
import requests

local_url = "http://localhost:1234/v1/styles/{}".format(sys.argv[1])

full_style_json = requests.get(local_url).json()

open(sys.argv[2], "w").write(json.dumps(full_style_json, indent=4))

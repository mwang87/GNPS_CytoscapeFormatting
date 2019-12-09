import requests

PRODUCTION_URL = "gnps-cytoscape.ucsd.edu"

def test_production():
    url = f"https://{PRODUCTION_URL}/process"
    params = {"task": "1ad7bc366aef45ce81d2dfcca0a9a5e7", "force": ""}

    r = requests.post(url, params=params)
    r.raise_for_status()

    redirect_url = r.json()["redirect_url"]
    visualization_url = f"https://{PRODUCTION_URL}/{redirect_url}"

    print(visualization_url)

    r = requests.get(visualization_url)

    r.raise_for_status()
import requests
import json
import os

def get_graph(id: str):
    http_response = requests.get(
        'https://www.virustotal.com/api/v3/graphs/{}'.format(id),
        headers = {'x-apikey' : os.environ['VIRUSTOTAL_API_KEY']}
    )
    if not http_response.ok:
        raise ConnectionError("Status Code: {}".format(http_response.status_code))
    return json.loads(http_response.text)

def get_full_url(id : str):
    http_response = requests.get(
        'https://www.virustotal.com/api/v3/urls/{}'.format(id),
        headers = {'x-apikey' : os.environ['VIRUSTOTAL_API_KEY']}
    )
    if not http_response.ok:
        raise ConnectionError("Status Code: {}".format(http_response.status_code))
    return json.loads(http_response.text)
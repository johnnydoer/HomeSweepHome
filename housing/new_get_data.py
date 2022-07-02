import requests
import json
from pprint import pprint

from auth import token


URL = "https://mightyzeus.housing.com/api/gql/stale?apiName=SEARCH_RESULTS&isBot=false&source=web"

with open("post2.json", "r") as f:
    json_data = json.load(f)


vars = json.loads(json_data["variables"])
vars["pageInfo"]["page"] = 2


json_data["variables"] = json.dumps(vars)

a = requests.post(URL, headers=token, json=json_data)
pprint(a.json())

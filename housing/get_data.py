import requests
import json
from pprint import pprint

from auth import token


URL = "https://mightyzeus.housing.com/api/gql/stale?apiName=SEARCH_RESULTS&isBot=false&source=web"


def post_request_body(filename: str):
    with open(filename, "r") as f:
        response_json_data = json.load(f)
        return response_json_data


def define_page_number(res_json_data, pageNumber: int):
    vars = json.loads(res_json_data["variables"])
    vars["pageInfo"]["page"] = pageNumber


def main():
    # TODO: Check with post.json (without cursor so probablty 1st request)
    # Check with post.json and post2.json (shouldn't work)
    # Hope post3.json works and if doesn't work then catch the 1st request with new cursor and compare with post3.json.
    res_json_data = post_request_body("post3.json")

    json_data = define_page_number(res_json_data, 1)

    json_data["variables"] = json.dumps(vars)

    a = requests.post(URL, headers=token, json=json_data)
    pprint(a.json())


if __name__ == "__main__":
    main()

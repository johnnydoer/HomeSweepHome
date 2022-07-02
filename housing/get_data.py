import requests
import json
from pprint import pprint

from headers import headers


def post_request_body(filename: str):
    with open(filename, "r") as f:
        request_body = json.load(f)
        return request_body


def post_request_with_cursor_body(filename: str, page_number: int, cursor: str):
    with open(filename, "r") as f:
        request_body = json.load(f)

    modified_request_body = set_request_variables(request_body, page_number, cursor)

    return modified_request_body


def set_request_variables(json_data, page_number: int, cursor: str):
    body_variables = json.loads(
        json_data["variables"]
    )  # Load body `variables` as JSON,
    body_variables["pageInfo"]["page"] = page_number  # Change page number,
    body_variables["meta"]["api"]["cursor"] = cursor  # Change cursor,

    json_data["variables"] = json.dumps(
        body_variables
    )  # Convert `variables` back to string in request body.

    return json_data


def get_housing_data(URL: str, request_json):
    server_response = requests.post(URL, headers=headers, json=request_json)
    return server_response.json()


def save_properties_to_db(housing_properties):
    pass


def main():
    URL = "https://mightyzeus.housing.com/api/gql/stale?apiName=SEARCH_RESULTS&isBot=false&source=web"
    request_json = post_request_body("post_without_cursor.json")

    response_json = get_housing_data(URL, request_json)

    housing_properties = response_json["data"]["searchResults"]["properties"]

    save_properties_to_db(housing_properties)

    cursor = response_json["data"]["searchResults"]["meta"]["api"]["cursor"]

    request_json = post_request_with_cursor_body("post_with_cursor.json", 20, cursor)

    response_json = get_housing_data(URL, request_json)

    housing_properties = response_json["data"]["searchResults"]["properties"]

    page = response_json["data"]["searchResults"]["config"]["pageInfo"]
    pprint(page)


if __name__ == "__main__":
    main()

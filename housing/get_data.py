import requests
import json
from pprint import pprint
from time import sleep

from headers import headers

import psycopg2


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


def convert_properties_to_schema(housing_properties):
    schema_properties = []
    for property in housing_properties:
        details = []
        details.append(str(property["title"]))
        details.append(str(property["subtitle"]))
        details.append(str(property["isActiveProperty"]))
        details.append(str(property["displayPrice"]["value"][0]))
        details.append(str(property["displayPrice"]["displayValue"]))
        details.append(str(property["url"]))
        details.append(str(property["listingId"]))
        details.append(str(property["originalListingId"]))
        if property["propertyInformation"]["bedrooms"] != None:
            details.append(str(property["propertyInformation"]["bedrooms"]))
        else:
            details.append("0")
        if property["propertyInformation"]["bathrooms"] != None:
            details.append(str(property["propertyInformation"]["bathrooms"]))
        else:
            details.append("0")
        if property["propertyInformation"]["parking"] != None:
            details.append(str(property["propertyInformation"]["parking"]))
        else:
            details.append("0")
        details.append(str(property["propertyInformation"]["area"]))
        details.append(str(property["propertyInformation"]["price"]))
        details.append(str(property["builtUpArea"]["value"]))
        details.append(str(property["builtUpArea"]["unit"]))
        details.append(str(property["emi"]))
        # details.append(str(property["description"]["overviewDescription"]))

        pprint(details)
        schema_properties.append(tuple(details))

    return schema_properties


def save_properties_to_db(housing_properties):
    while True:
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="zerodha_data",
                user="postgres",
                password="password",
            )
            break
        except psycopg2.OperationalError:
            sleep(2)
            print("Connection to DB failed.")

    conn.autocommit = True
    cur = conn.cursor()

    schema_housing_properties = convert_properties_to_schema(housing_properties)

    args = ",".join(
        cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", a).decode(
            "utf-8"
        )
        for a in schema_housing_properties
    )

    cur.execute(
        "INSERT INTO properties VALUES "
        + args
        + " ON CONFLICT ON CONSTRAINT property_listing DO NOTHING;"
    )

    conn.close()


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

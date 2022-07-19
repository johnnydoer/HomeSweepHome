import requests
import json
from pprint import pprint
from time import sleep

from headers import headers

import psycopg2

# 1st request body for Housing GraphQL.
def post_request_body(filename: str):
    with open(filename, "r") as f:  # Open file with the POST requests body JSON data.
        request_body = json.load(f)
        return request_body


# Subsequent request body for Housing GraphQL.
def post_request_with_cursor_body(filename: str, page_number: int, cursor: str):
    with open(
        filename, "r"
    ) as f:  # Open file with the POST requests body JSON data (contains cursor).
        request_body = json.load(f)

    modified_request_body = set_request_variables(
        request_body, page_number, cursor
    )  # Changed JSON variables for new request.

    return modified_request_body


# Change page number and cursor in JSON for every new request.
def set_request_variables(json_data, page_number: int, cursor: str):
    body_variables = json.loads(
        json_data["variables"]
    )  # Load body `variables` as JSON,
    body_variables["pageInfo"]["page"] = page_number  # Change page number.
    body_variables["meta"]["api"]["cursor"] = cursor  # Change cursor.

    json_data["variables"] = json.dumps(
        body_variables
    )  # Convert `variables` back to string in request body.

    return json_data


# Request Housing GraphQL.
def get_housing_data(URL: str, request_json):
    server_response = requests.post(URL, headers=headers, json=request_json)
    return server_response.json()


# Convert data coming from Housing according to SQL Schema.
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
        details.append(str(property["coords"][0]))
        details.append(str(property["coords"][1]))
        if property["propertyInformation"]["bedrooms"] not in ["", None]:
            details.append(str(property["propertyInformation"]["bedrooms"]))
        else:
            details.append(None)
        if property["propertyInformation"]["bathrooms"] not in ["", None]:
            details.append(str(property["propertyInformation"]["bathrooms"]))
        else:
            details.append(None)
        if property["propertyInformation"]["parking"] not in ["", None]:
            details.append(str(property["propertyInformation"]["parking"]))
        else:
            details.append(None)
        details.append(str(property["propertyInformation"]["area"]))
        details.append(str(property["propertyInformation"]["price"]))
        details.append(str(property["builtUpArea"]["value"]))
        details.append(str(property["builtUpArea"]["unit"]))
        details.append(str(property["emi"]))

        schema_properties.append(tuple(details))

    return schema_properties


# Save converted datra to SQL.
def save_properties_to_db(housing_properties):
    while True:  # Try connection to DB and if failed, try again with error display.
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="housing",
                user="postgres",
                password="password",
            )  # DB credentials. TODO: Take from .env file.
            break  # Break loop on successful connection.
        except psycopg2.OperationalError:
            sleep(2)
            print("Connection to DB failed.")

    conn.autocommit = True
    cur = conn.cursor()

    schema_housing_properties = convert_properties_to_schema(housing_properties)

    args = ",".join(
        cur.mogrify(
            "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", a
        ).decode("utf-8")
        for a in schema_housing_properties
    )  # Add all values to be added the the INSERT STATEMENT string.

    cur.execute(
        "INSERT INTO properties VALUES "
        + args
        + """ ON CONFLICT ON CONSTRAINT property_listing
        DO NOTHING"""
        # SET (title,subtitle,is_active_property,display_price,display_value,url,listing_id,original_listing_id,bedrooms,bathrooms,parking,area,price,built_up_area_value,built_up_area_unit,emi) = (EXCLUDED.title,EXCLUDED.subtitle,EXCLUDED.is_active_property,EXCLUDED.display_price,EXCLUDED.display_value,EXCLUDED.url,EXCLUDED.listing_id,EXCLUDED.original_listing_id,EXCLUDED.bedrooms,EXCLUDED.bathrooms,EXCLUDED.parking,EXCLUDED.area,EXCLUDED.price,EXCLUDED.built_up_area_value,EXCLUDED.built_up_area_unit,EXCLUDED.emi);"""
    )  # Fastest way to insert multiple rows to PostgreSQL.

    conn.close()  # Always close connections. :)


def main():
    # TODO: Add the below to a function.

    # Set URL for requests.
    URL = "https://mightyzeus.housing.com/api/gql/stale?apiName=SEARCH_RESULTS&isBot=false&source=web"

    request_json = post_request_body(
        "post_without_cursor.json"
    )  # 1st request to housing.com without cursor.

    response_json = get_housing_data(
        URL, request_json
    )  # Response for 1st request. TODO: Add proper checks.

    housing_properties = response_json["data"]["searchResults"][
        "properties"
    ]  # Getting properties from the response JSON data. TODO: Add proper checks.

    save_properties_to_db(housing_properties)  # Save data to DB.

    cursor = response_json["data"]["searchResults"]["meta"]["api"][
        "cursor"
    ]  # Getting cursor from the response JSON data. TODO: Add proper checks.

    page_number = 1  # Initialise page number.

    # Loop for all subsequent requests according to page number.
    while True:
        try:
            request_json = post_request_with_cursor_body(
                "post_with_cursor.json", page_number, cursor
            )

            response_json = get_housing_data(URL, request_json)

            # pprint(response_json)
            if "errors" in response_json:
                break

            housing_properties = response_json["data"]["searchResults"]["properties"]

            save_properties_to_db(housing_properties)

            cursor = response_json["data"]["searchResults"]["meta"]["api"]["cursor"]

            print("Page number {} completed.".format(page_number))

            page_number = page_number + 1

            # DEBUG:
            if page_number == 10:
                break
        except Exception as e:
            pprint(e)
            break


if __name__ == "__main__":
    main()

import json

from db_service import insert_item, get_item
from request_validation_utils import validate_body_license, validate_property_exist
from request_response_utils import return_error_response, return_status_ok

ENV_TABLE_NAME = "dermoapp-doctor"


def handler(event, context):
    try:
        print("lambda execution with context {0}".format(str(context)))
        if validate_property_exist("doctor_id", event['pathParameters']) and validate_property_exist('body', event):
            if validate_body_license(event['body']):
                doctor_id = event['pathParameters']['doctor_id']
                response = add_doctor_license(event, doctor_id)
                return return_status_ok(response)
        else:
            return return_error_response("missing or malformed request body", 412)
    except Exception as err:
        return return_error_response("cannot proceed with the request error: " + str(err), 500)


def add_doctor_license(request, doctor_id):
    parsed_body = json.loads(request["body"])
    registry = {
        "doctor_id": doctor_id,
        "license_number": str(parsed_body['license_number']),
        "status": get_status_from_license(str(parsed_body['license_number']))
    }
    if insert_item(registry):
        persisted_data = get_item("doctor_id", doctor_id)
        return persisted_data


def get_status_from_license(license):
    if "-verif" in license:
        return "Verified"
    if "-rej" in license:
        return "Rejected"
    return "Pending"

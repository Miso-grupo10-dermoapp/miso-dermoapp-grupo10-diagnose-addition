import json
import uuid

from datetime import date
from db_service import insert_item, get_item
from request_validation_utils import validate_body_params, validate_property_exist
from request_response_utils import return_error_response, return_status_ok

ENV_TABLE_NAME = "dermoapp-patient-diagnoses"


def handler(event, context):
    try:
        print("lambda execution with context {0}".format(str(context)))
        if validate_property_exist("patient_id", event['pathParameters']) and validate_property_exist("case_id", event[
            'pathParameters']):
            if validate_property_exist('body', event) and validate_body_params(event['body']):
                response = add_diagnose(event)
                return return_status_ok(response)
        else:
            return return_error_response("missing or malformed request body", 412)
    except Exception as err:
        return return_error_response("cannot proceed with the request error: " + str(err), 500)


def add_diagnose(request):
    parsed_body = json.loads(request["body"])
    parsed_body['case_id'] = request['pathParameters']['case_id']
    parsed_body['patient_id'] = request['pathParameters']['patient_id']
    parsed_body['diagnose_id'] = str(uuid.uuid4())
    parsed_body['creation_date'] = str(date.today())

    if insert_item(parsed_body):
        persisted_data = get_item("diagnose_id", parsed_body['diagnose_id'])
        return persisted_data

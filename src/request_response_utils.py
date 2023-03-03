import json


def return_error_response(error_message, http_code):
    return {
        "statusCode": http_code,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'content-type': 'application/json'
        },
        "body": json.dumps(
            {
                "message": error_message
            }
        ),
    }


def return_status_ok(response_body):
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'content-type': 'application/json'
        },
        "body": json.dumps(response_body),
    }


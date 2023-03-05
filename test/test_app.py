import json
import os

import boto3
from boto3.dynamodb.conditions import Key
import moto
import pytest

import app
from request_validation_utils import body_properties

TABLE_NAME = "dermoapp-patient-diagnoses"


@pytest.fixture
def lambda_environment():
    os.environ[app.ENV_TABLE_NAME] = TABLE_NAME


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def data_table(aws_credentials):
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            KeySchema=[
                {"AttributeName": "diagnose_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "diagnose_id", "AttributeType": "S"},
            ],
            TableName=TABLE_NAME,
            BillingMode="PAY_PER_REQUEST"
        )

        yield TABLE_NAME


def test_givenValidInputRequestThenReturn200AndValidPersistence(lambda_environment, data_table):
    event = {
        "resource": "/doctor/{patient_id}/diagnose/{case_id}",
        "path": "/doctor/123/diagnose/567-verif",
        "httpMethod": "POST",
        "pathParameters": {
            "patient_id": "123",
            "case_id": "567-verif"
        },
        "body": "{\n    \"doctor_id\": \"2343536556\", \"doctor_name\": \"dr.test\", \"diagnose\": \"test\" \n}",
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    lambdaBodyResponse= json.loads(lambdaResponse['body'])
    client = boto3.resource("dynamodb", region_name="us-east-1")
    mockTable = client.Table(TABLE_NAME)
    response = mockTable.query(
        KeyConditionExpression=Key('diagnose_id').eq(lambdaBodyResponse['diagnose_id'])
    )
    items = response['Items']
    if items:
        data = items[0]

    assert lambdaResponse['statusCode'] == 200
    assert data is not None
    for property in body_properties:
        assert data[property] is not None
        assert data[property] == lambdaBodyResponse[property]

def test_givenMissingLicenseNumberOnRequestThenReturnError500(lambda_environment, data_table):
    event = {
        "resource": "/doctor/{patient_id}/diagnose/{case_id}",
        "path": "/doctor/123/diagnose/567-verif",
        "httpMethod": "POST",
        "pathParameters": {
            "patient_id": "123",
            "case_id": "567-verif"
        },
        "body": "{\n    \"doctor_id\": \"2343536556\", \"doctor_name\": \"dr.test\" \n}",
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 500
    assert "cannot proceed with the request error: Input request is malformed or missing parameters," in lambdaResponse['body']


def test_givenMalformedRequestOnRequestThenReturnError412(lambda_environment, data_table):
    event = {
        "resource": "/doctor/{patient_id}/diagnose/{case_id}",
        "path": "/doctor/123/diagnose/567-verif",
        "httpMethod": "POST",
        "pathParameters": {
            "case_id": "567-verif"
        },
        "body": "{\n    \"doctor_id\": \"2343536556\", \"doctor_name\": \"dr.test\", \"diagnose\": \"test\" \n}",
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 412
    assert lambdaResponse['body'] == '{"message": "missing or malformed request body"}'

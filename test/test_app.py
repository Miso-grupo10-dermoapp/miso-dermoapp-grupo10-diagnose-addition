import json
import os

import boto3
from boto3.dynamodb.conditions import Key
import moto
import pytest

import app

TABLE_NAME = "dermoapp-doctor"
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
            AttributeDefinitions=[
                {"AttributeName": "doctor_id", "AttributeType": "S"},
                {"AttributeName": "license_number", "AttributeType": "S"}
            ],
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "doctor_id", "KeyType": "HASH"},
                {"AttributeName": "license_number", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield TABLE_NAME

def test_givenValidInputRequestThenReturn200AndValidPersistence(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/123/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{\n    \"license_number\": \"234353-verif\" \n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    client = boto3.resource("dynamodb", region_name="us-east-1")
    mockTable = client.Table(TABLE_NAME)
    response = mockTable.query(
        KeyConditionExpression= Key('doctor_id').eq('123')
    )
    items = response['Items']
    if items:
        data = items[0]

    assert lambdaResponse['statusCode'] == 200
    assert lambdaResponse['body'] ==  '{"doctor_id": "123", "license_number": "234353-verif", "status": "Verified"}'
    assert data is not None
    assert data['doctor_id'] is not None
    assert data['license_number'] is not None
    assert data['doctor_id'] == '123'
    assert data['license_number'] == "234353-verif"

def test_givenValidInputRequestWithRejectedStatusThenReturn200AndValidPersistence(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/123/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{\n    \"license_number\": \"234353-rej\" \n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    client = boto3.resource("dynamodb", region_name="us-east-1")
    mockTable = client.Table(TABLE_NAME)
    response = mockTable.query(
        KeyConditionExpression= Key('doctor_id').eq('123')
    )
    items = response['Items']
    if items:
        data = items[0]

    assert lambdaResponse['statusCode'] == 200
    assert lambdaResponse['body'] ==  '{"doctor_id": "123", "license_number": "234353-rej", "status": "Rejected"}'
    assert data is not None
    assert data['doctor_id'] is not None
    assert data['license_number'] is not None
    assert data['doctor_id'] == '123'
    assert data['license_number'] == "234353-rej"

def test_givenValidInputRequestWithRejectedStatusThenReturn200AndValidPersistence(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/123/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{\n    \"license_number\": \"234353\" \n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    client = boto3.resource("dynamodb", region_name="us-east-1")
    mockTable = client.Table(TABLE_NAME)
    response = mockTable.query(
        KeyConditionExpression= Key('doctor_id').eq('123')
    )
    items = response['Items']
    if items:
        data = items[0]

    assert lambdaResponse['statusCode'] == 200
    assert lambdaResponse['body'] ==  '{"doctor_id": "123", "license_number": "234353", "status": "Pending"}'
    assert data is not None
    assert data['doctor_id'] is not None
    assert data['license_number'] is not None
    assert data['doctor_id'] == '123'
    assert data['license_number'] == "234353"
def test_givenMissingLicenseNumberOnRequestThenReturnError500(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/123/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])


    assert lambdaResponse['statusCode'] == 500
    assert lambdaResponse['body'] ==  '{"message": "cannot proceed with the request error: Input request is malformed or missing parameters, details license cannot be empty"}'

def test_givenMalformedRequestOnRequestThenReturnError412(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/license",
            "httpMethod": "POST",
            "pathParameters": {
            },
            "body": "{\n    \"license_number\": \"234353\" \n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])


    assert lambdaResponse['statusCode'] == 412
    assert lambdaResponse['body'] == '{"message": "missing or malformed request body"}'

def test_givenNonValidBodyRequestThenReturnError500(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{\n    \"other_field\": 234353\n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])


    assert lambdaResponse['statusCode'] == 500
    assert lambdaResponse['body'] == '{"message": "cannot proceed with the request error: Input request is malformed or missing parameters, details license cannot be empty"}'

def test_givenRequestWithoutBodyThenReturnError412(lambda_environment, data_table):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": None,
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])


    assert lambdaResponse['statusCode'] == 412
    assert lambdaResponse['body'] == '{"message": "missing or malformed request body"}'

def test_givenValidRequestAndDBFailureThenReturn500(lambda_environment):

    event = {
            "resource": "/doctor/{doctor_id}/license",
            "path": "/doctor/license",
            "httpMethod": "POST",
            "pathParameters": {
                "doctor_id": "123"
            },
            "body": "{\n    \"license_number\": 234353\n}",
            "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])


    assert lambdaResponse['statusCode'] == 500
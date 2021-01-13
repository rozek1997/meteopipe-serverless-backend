import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEVICE_STATUS_TABLE_NAME = os.environ.get("DEVICE_STATUS_TABLE")
dynamodb = boto3.resource("dynamodb")
DEVICE_TABLE = dynamodb.Table(DEVICE_STATUS_TABLE_NAME)


def lambda_handler(event, context):
    response = load_table()

    return json.dumps(response)


def load_table():
    logger.info("Start reading from status table")
    response = DEVICE_TABLE.scan()
    data = response["Items"]

    return {
        "statusCode": 200,
        "deviceStatus": data
    }

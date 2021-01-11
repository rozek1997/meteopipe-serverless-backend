import logging
import os

import boto3

HISTORY_TABLE_NAME = os.environ.get("HISTORY_TABLE")
STATUS_TABLE_NAME = os.environ.get("STATUS_TABLE")

dynamodb = boto3.resource("dynamodb")
STATUS_TABLE = dynamodb.Table(STATUS_TABLE_NAME)
HISTORY_TABLE = dynamodb.Table(HISTORY_TABLE_NAME)

dynamodb_client = boto3.client("dynamodb")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, contect):
    message = {}
    message = event
    logger.info("Message from device: {}".format(message))
    location_string = message["location"]

    history_item = {key: value for (key, value) in message.items() if key != "deviceId" or key != "timestamp"}
    history_item["deviceID"] = message["deviceId"]
    history_item["timestamp"] = message["timestamp"]

    write_to_history_table(history_item)
    history_item["location"] = location_string
    write_to_status_table(history_item)


def write_to_history_table(item: dict):
    item.pop("location", None)
    item.pop("deviceId", None)
    HISTORY_TABLE.put_item(Item=item)


def write_to_status_table(item: dict):
    item.pop("deviceId", None)
    STATUS_TABLE.put_item(Item=item)

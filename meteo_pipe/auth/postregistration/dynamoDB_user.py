import logging
import os
import time

import boto3

logging.basicConfig(level=logging.INFO)
dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context, callback):
    logger = logging.getLogger()

    date = time.time()
    table_name = os.environ.get("TABLE_NAME")
    region = os.environ.get("REGION")

    logger.info(event)

    user_UUID = event["userName"]
    userAttr = event["request"]["userAttributes"]

    dynamodb_client.put_item(TableName=table_name, Item={
        "UID": {"S": user_UUID},
        "email": {"S": userAttr["email"]},
        "name": {"S": userAttr["name"]},
        # "createdAt": {"S": date}
    })

    callback(None, user_UUID)

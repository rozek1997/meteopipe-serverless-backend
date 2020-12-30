import logging
import os
import time

import boto3

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    logger = logging.getLogger()
    dynamodb_client = boto3.client("dynamodb")
    date = time.time()
    table_name = os.environ.get("TABLE_NAME")
    region = os.environ.get("REGION")

    logger.info(event)
    logger.info(time)

    userAttr = event["request"]["userAttributes"]

    dynamodb_client.put_item(TableName=table_name, Item={
        "UID": {"S": event["userName"]},
        "email": {"S": userAttr["email"]},
        "name": {"S": userAttr["name"]},
        # "createdAt": {"S": date}
    })

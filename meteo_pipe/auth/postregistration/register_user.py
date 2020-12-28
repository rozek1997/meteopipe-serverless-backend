import logging
import os
import time

import boto3

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    logger = logging.getLogger()
    dynamodb = boto3.client("dynamodb")
    date = time.time()
    table_name = os.environ.get("TABLE_NAME")
    region = os.environ.get("REGION")

    logger.info(event)

    userAttr = event["request"]["userAttributes"]

    dynamodb.put_item(TableName=table_name, Item={
        "UID": {"S": event["userName"]},
        "email": {"S": userAttr["email"]},
        "name": {"S": userAttr["name"]},
        # "createdAt": {"S": date}
    })

    # context.done(None, event)

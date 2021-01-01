import logging
import os
from datetime import datetime

import boto3

logging.basicConfig(level=logging.INFO)
dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):
    logger = logging.getLogger()

    date = datetime.now()
    table_name = os.environ.get("TABLE_NAME")
    region = os.environ.get("REGION")

    logger.info(event)

    user_UUID = event["userName"]
    userAttr = event["request"]["userAttributes"]

    dynamodb_client.put_item(TableName=table_name, Item={
        "UID": {"S": user_UUID},
        "email": {"S": userAttr["email"]},
        "name": {"S": userAttr["name"]},
        "createdAt": {"S": str(date)}
    })

    return {
        "userd_UUID": user_UUID
    }

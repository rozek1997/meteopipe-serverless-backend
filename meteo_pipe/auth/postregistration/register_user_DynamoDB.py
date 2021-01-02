import logging
import os
from datetime import datetime

import boto3

dynamodb_client = boto3.client("dynamodb")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    date = datetime.now()
    table_name = os.environ.get("TABLE_NAME")
    # region = os.environ.get("REGION")

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
        "user_UUID": user_UUID
    }

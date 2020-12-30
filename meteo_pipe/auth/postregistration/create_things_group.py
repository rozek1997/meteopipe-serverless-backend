import logging
import os

import boto3

iot_client = boto3.client("iot")
iot_parent_group_name = os.environ.get("IoTParentGroupName")


def lambda_handler(event, context, callback):
    logger = logging.getLogger()

    user_UUID = event["user_UUID"]

    thingGroupProperties = {
        "thingGroupDescription": "thing group for user devices with uuid {}".format(user_UUID)
    }

    response = iot_client.create_thing_group(
        thingGroupName=user_UUID,
        parentGroupName=iot_parent_group_name,
        thingGroupProperties=thingGroupProperties
    )

    callback(None, None)

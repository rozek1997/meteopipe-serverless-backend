import json
import logging
import os

import boto3

iot_client = boto3.client("iot")
iot_parent_group_name = os.environ.get("IoTParentGroupName")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    user_UUID = event["user_UUID"]
    thing_group = create_thing_group(user_UUID)
    thing_policy = create_thing_policy(user_UUID)
    print(thing_group)
    print(thing_policy)


def create_thing_group(user_uuid: str):
    thingGroupProperties = {
        "thingGroupDescription": "thing group for user devices with uuid {}".format(user_uuid)
    }

    response = iot_client.create_thing_group(
        thingGroupName=user_uuid,
        parentGroupName=iot_parent_group_name,
        thingGroupProperties=thingGroupProperties
    )

    return response


def create_thing_policy(user_uuid: str):
    policy_name = "meteopipe-user-policy-{}".format(user_uuid)

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "iot:Connect",
                "Resource": "arn:aws:iot:eu-central-1:045341403599:client/meteopipe-thing/" + user_uuid + "/${iot:Connection.Thing.ThingName}"
            },
            {
                "Effect": "Allow",
                "Action": "iot:Subscribe",
                "Resource": "arn:aws:iot:eu-central-1:045341403599:topicfilter/meteopipe-thing/" + user_uuid + "/${iot:Connection.Thing.ThingName}"
            },
            {
                "Effect": "Allow",
                "Action": "iot:Publish",
                "Resource": "arn:aws:iot:eu-central-1:045341403599:topic/meteopipe-thing/" + user_uuid + "/${iot:Connection.Thing.ThingName}"
            },
            {
                "Effect": "Allow",
                "Action": "iot:Receive",
                "Resource": "arn:aws:iot:eu-central-1:045341403599:topic/meteopipe-thing/" + user_uuid + "/${iot:Connection.Thing.ThingName}"
            }
        ]
    }

    response = iot_client.create_policy(
        policyName=policy_name,
        policyDocument=json.dumps(policy_document),
        tags=[
            {
                "Key": "used-for",
                "Value": "meteopipe-app"
            }
        ]
    )

    return response

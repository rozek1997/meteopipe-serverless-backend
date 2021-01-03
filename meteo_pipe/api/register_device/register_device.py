import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
iot_client = boto3.client("iot")
dynamo_client = boto3.client("dynamodb")

user_uuid = ""
thing = {}
cert_and_keys = {}

policy_name_core = "meteopipe-user-policy-{}"
endpoints = {
    "connect_endpoint": os.environ.get("IoTEndpointConnect"),
    "subscribe_endpoint": os.environ.get("IoTEndpointSubscribe"),
    "publish_endpoint": os.environ.get("IoTEndpointPublish")
}


def lambda_handler(event, context):
    global user_uuid
    user_uuid = event["uuid"]
    things_name = event["thing_name"]
    answer = {}


def generate_device_cert():
    global cert_and_keys
    cert_and_keys = iot_client.create_keys_and_certificate(setAsActive=True)


def generate_CA_cert():
    pass


def attach_policy_to_cert():
    policy_name = policy_name_core.format(user_uuid)
    iot_client.attachPolicy(
        policyName=policy_name,
        target=cert_and_keys["certificateArn"]
    )


def create_thing(thing_name: str):
    global thing
    thing = iot_client.create_thing(thingName=thing_name)


def attach_thing_to_thing_group():
    thing_group = iot_client.describe_thing_group(
        thingGroupName=user_uuid
    )
    iot_client.add_thing_to_thing_group(
        thingGroupName=thing_group["thingGroupName"],
        thingGroupArn=thing_group["thingGroupArn"],
        thingName=thing["thingName"],
        thingArn=thing["thingArn"]
    )


def define_thing_endpoint():
    global endpoints
    endpoints["connect_endpoint"] = endpoints["connect_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"
    endpoints["subscribe_endpoint"] = endpoints["subscribe_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"
    endpoints["publish_endpoint"] = endpoints["publish_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"


def create_config_file():
    pass

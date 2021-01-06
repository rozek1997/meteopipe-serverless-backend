import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

iot_client = boto3.client("iot")


def lambda_handler(event, context):
    request_body = json.loads(event["body"])
    user_uuid = request_body["uuid"]

    logger.info("Request body {}".format(request_body))
    thing_group_name = user_uuid
    answer = {"headers": "Content-Type': 'application/json"}
    try:
        device_list = list_user_devices(thing_group_name)
        answer["statusCode"] = 200
        answer["body"] = json.dumps({"device_list": device_list})
    except Exception as error:
        answer["statusCode"] = 400
        answer["body"] = json.dumps({"errorMessage": str(error)})
    except iot_client.exceptions.ResourceNotFoundException as error:
        answer["statusCode"] = 404
        answer["body"] = json.dumps({"errorMessage": str(error)})

    return answer


def list_user_devices(group_name: str):
    device_list = []
    logger.info("loading devices list from iot core for group {}".format(group_name))
    token = None
    while 1:
        if token is not None:
            response = iot_client.list_things_in_thing_group(
                thingGroupName=group_name,
                recursive=False,
                nextToken=token,
                maxResults=20)
        else:
            response = iot_client.list_things_in_thing_group(
                thingGroupName=group_name,
                recursive=False,
                maxResults=20)

        logger.info("Response from iot core for group {}: {}".format(group_name, response))
        device_list.extend(response["things"])
        if "nextToken" not in response:
            break
        else:
            token = response["nextToken"]

    return device_list

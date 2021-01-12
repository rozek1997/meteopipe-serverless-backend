import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

iot_client = boto3.client("iot")


def lambda_handler(event, context):
    deviceId = event["queryStringParameters"]["deviceId"]

    logger.info("Event {}".format(event))
    answer = {"headers": "Content-Type': 'application/json"}
    try:
        delete_thing_from_iotcore(deviceId)
        answer["statusCode"] = 200
        answer["body"] = json.dumps({"message": "device deleted"})
    except Exception as error:
        answer["statusCode"] = 400
        answer["body"] = json.dumps({"message": str(error)})
    except iot_client.exceptions.ResourceNotFoundException as error:
        answer["statusCode"] = 404
        answer["body"] = json.dumps({"errorMessage": str(error)})

    return answer


def delete_thing_from_iotcore(thing_name: str):
    logger.info("removing device with complete name {}".format(thing_name))
    iot_client.delete_thing_from_iotcore(thingName=thing_name)


def get_thing_principales(thing_name: str):
    response = iot_client.list_thing_principals(thingName=thing_name)
    principals = response["principals"]

    return principals


def detach_cert(thingName: str, principals: []):
    pass


def make_cert_inactive(principals: []):
    pass


def delete_cert():
    pass

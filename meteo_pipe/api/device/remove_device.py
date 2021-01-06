import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

iot_client = boto3.client("iot")


def lambda_handler(event, context):
    request_body = json.loads(event["body"])
    user_uuid = request_body["uuid"]
    thing_name = request_body["thing_name"]

    logger.info("Request body {}".format(request_body))
    complete_thing_name = user_uuid + "-" + thing_name
    answer = {"headers": "Content-Type': 'application/json"}
    try:
        delete_thing(complete_thing_name)
        answer["statusCode"] = 200
        answer["body"] = json.dumps({"message": "device deleted"})
    except Exception as error:
        answer["statusCode"] = 400
        answer["body"] = json.dumps({"message": str(error)})
    except iot_client.exceptions.ResourceNotFoundException as error:
        answer["statusCode"] = 404
        answer["body"] = json.dumps({"errorMessage": str(error)})

    return answer


def delete_thing(thing_name: str):
    logger.info("removing device with complete name {}".format(thing_name))
    iot_client.delete_thing(thingName=thing_name)

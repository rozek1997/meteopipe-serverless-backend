import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

iot_client = boto3.client("iot")
POLICY_TEMPLATE = "meteopipe-user-policy-{}"
user_uuid = None


def lambda_handler(event, context):
    global user_uuid
    deviceId = event["queryStringParameters"]["deviceId"]
    user_uuid = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
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
    principals = get_thing_principales(thing_name)
    detach_user_policy(thing_name, principals)
    detach_cert(thing_name, principals)
    make_cert_inactive(principals)
    delete_cert(principals)
    iot_client.delete_thing_from_iotcore(thingName=thing_name)


def detach_user_policy(thing_name, principals: []):
    policy = POLICY_TEMPLATE.format(user_uuid)

    for principal in principals:
        iot_client.detach_policy(
            policyName=policy,
            target=principal
        )


def get_thing_principales(thing_name: str):
    response = iot_client.list_thing_principals(thingName=thing_name)
    principals = response["principals"]

    return principals


def detach_cert(thingName: str, principals: []):
    for principal in principals:
        iot_client.detach_thing_principal(
            thingName=thingName,
            principal=principal
        )


def get_cert_id_from_arn(certificate_arn: str):
    certificateId = certificate_arn.rsplit("/", 1)[-1]
    logger.info(certificateId)
    return certificateId


def make_cert_inactive(principals: []):
    for principal in principals:
        iot_client.update_certificate(
            certificateId=get_cert_id_from_arn(principal),
            newStatus="INACTIVE"
        )


def delete_cert(principals: []):
    for principal in principals:
        iot_client.delete_certificate(
            certificateId=get_cert_id_from_arn(principal),
        )

import json
import logging
import os

import boto3

step_function_client = boto3.client("stepfunctions")
step_function_ARN = os.environ.get("STEP_FUNCTION_ARN")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    step_function_ID = event["userName"]

    logger.info(event)
    # step_function_input = {"stepfunction_ID": step_function_ID, "payload": event}

    response = step_function_client.start_sync_execution(
        stateMachineArn=step_function_ARN,
        name=step_function_ID,
        input=json.dumps(event)
    )

    logger.info(response)
    step_function_status = response["status"]

    lambda_response = None

    if step_function_status == "SUCCEEDED":
        lambda_response["statusCode"] = 302
        lambda_response["headers"] = {"Location": "http://localhost:3000/sign-up"}

    logger.info(lambda_response)

    return lambda_response

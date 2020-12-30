import json
import logging
import os

import boto3

logging.basicConfig(level=logging.INFO)

step_function_client = boto3.client("stepfunctions")
step_function_ARN = os.environ.get("STEP_FUNCTION_ARN")


def lambda_handler(event, context):
    logger = logging.getLogger()

    step_function_ID = event["userName"]

    step_function_input = {"stepfunction_ID": step_function_ID, "payload": event}

    response = step_function_client.start_execution(
        stateMachineArn=step_function_ARN,
        name=step_function_ID,
        input=json.dumps(step_function_input)
    )

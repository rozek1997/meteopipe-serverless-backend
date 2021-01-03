import json
import logging
import os
import zipfile

import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
iot_client = boto3.client("iot")
dynamo_client = boto3.client("dynamodb")

CA_CERT_URL = [
    'https://www.amazontrust.com/repository/AmazonRootCA1.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA2.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA3.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA4.pem',
    'https://www.websecurity.digicert.com/content/dam/websitesecurity/digitalassets/desktop/pdfs/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem'
]
CONFIG_DIR_TEMPLATE = "/tmp/{}/"
POLICY_NAME_TEMPLATE = "meteopipe-user-policy-{}"
PUBLIC_KEY_FILE_TEMPLATE = "{}.public.key"
PRIVATE_KEY_FILE_TEMPLATE = "{}.private.key"
CERT_PEM_FILE_TEMPLATE = "{}.cert.pem"
CA_CERT_FILE_NAME = "root.ca.bundle.pem"
CONFIG_FILE_NAME = "config.json"
ZIP_FILE_NAME = "{}-meteopipe.zip"
user_uuid = "{}-meteopipe.zip"

endpoints = {
    "connect_endpoint": os.environ.get("IoTEndpointConnect"),
    "subscribe_endpoint": os.environ.get("IoTEndpointSubscribe"),
    "publish_endpoint": os.environ.get("IoTEndpointPublish")
}


def create_thing(thing_name: str):
    thing_name = user_uuid + "-" + thing_name
    thing = iot_client.create_thing(thingName=thing_name)
    return thing


def attach_thing_to_thing_group(thing: dict):
    thing_group = iot_client.describe_thing_group(
        thingGroupName=user_uuid
    )

    iot_client.add_thing_to_thing_group(
        thingGroupName=thing_group["thingGroupName"],
        thingGroupArn=thing_group["thingGroupArn"],
        thingName=thing["thingName"],
        thingArn=thing["thingArn"])


def generate_device_cert():
    cert_and_keys = iot_client.create_keys_and_certificate(setAsActive=True)
    return cert_and_keys


def attach_policy_to_cert(certificiate_arn: str):
    policy_name = POLICY_NAME_TEMPLATE.format(user_uuid)
    iot_client.attach_policy(
        policyName=policy_name,
        target=certificiate_arn
    )


def create_user_config_dir():
    global CONFIG_DIR_TEMPLATE
    CONFIG_DIR_TEMPLATE = CONFIG_DIR_TEMPLATE.format(user_uuid)
    os.mkdir(path=CONFIG_DIR_TEMPLATE, mode=0o777)


def generate_ca_cert():
    ca_cert_path = CONFIG_DIR_TEMPLATE + CA_CERT_FILE_NAME
    with open(ca_cert_path, "wb") as CA_FILE:
        for url in CA_CERT_URL:
            response = requests.get(url)
            CA_FILE.write(response.content)

    CA_FILE.close()


def generate_cert_and_key_files(cert_and_keys: dict):
    public_key_file = CONFIG_DIR_TEMPLATE + PUBLIC_KEY_FILE_TEMPLATE.format(user_uuid)
    private_key_file = CONFIG_DIR_TEMPLATE + PRIVATE_KEY_FILE_TEMPLATE.format(user_uuid)
    certificate_pem_file = CONFIG_DIR_TEMPLATE + CERT_PEM_FILE_TEMPLATE.format(user_uuid)

    logger.info("start saving public keys and cert to {}".format(public_key_file))
    with open(public_key_file, "w") as PUBLIC_KEY_FILE:
        PUBLIC_KEY_FILE.write(cert_and_keys["keyPair"]["PublicKey"])
    with open(private_key_file, "w") as PRIVATE_KEY_FILE:
        PRIVATE_KEY_FILE.write(cert_and_keys["keyPair"]["PrivateKey"])
    with open(certificate_pem_file, "w") as CERT_PEM_FILE:
        CERT_PEM_FILE.write(cert_and_keys["certificatePem"])

    PUBLIC_KEY_FILE.close()
    PRIVATE_KEY_FILE.close()
    CERT_PEM_FILE.close()

    return


def define_config_json():
    config = {
        "endpoints": endpoints,
        "public_key_path": "",
        "private_key_path": "",
        "cert_path": "",
        "ca_cert_path": ""

    }

    return json.dumps(config)


def generate_config_file(config: str):
    config_file_name = CONFIG_DIR_TEMPLATE + CONFIG_FILE_NAME
    os.chdir(CONFIG_DIR_TEMPLATE)
    configuration_json = json.dumps(config)
    with open(config_file_name, "w") as CONFIG_FILE:
        CONFIG_FILE.write(configuration_json)

    CONFIG_FILE.close()


def define_thing_endpoint():
    global endpoints
    endpoints["connect_endpoint"] = endpoints["connect_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"
    endpoints["subscribe_endpoint"] = endpoints["subscribe_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"
    endpoints["publish_endpoint"] = endpoints["publish_endpoint"] + user_uuid + "/${iot:Connection.Thing.ThingName}"


def provision_device(thing_name: str):
    answer = {}
    logger.info("thing_name: {}, uuid: {}".format(thing_name, user_uuid))

    # section of provisioning device
    try:
        thing = create_thing(thing_name)
        attach_thing_to_thing_group(thing)
        cert_and_keys = generate_device_cert()
        attach_policy_to_cert(cert_and_keys["certificateArn"])
    except Exception as error:
        logger.error("Cant create thing with thing name {}, error message {}".format(thing_name, error))
        answer["status"] = "error"
        answer["message"] = "error creating thing"
    else:  # section of preparing answer
        logger.info("creating {} user files for thing {}".format(user_uuid, thing_name))
        create_user_config_dir()
        generate_ca_cert()
        generate_cert_and_key_files(cert_and_keys)
        define_thing_endpoint()
        config_template = define_config_json()
        generate_config_file(config_template)
        generate_zip_file()

        answer["statusCode"] = 200
        answer['isBase64Encoded']: True
        answer["headers"] = {
            'Content-Type': 'application/zip, application/octet-stream',
            'Content-disposition': f"attachment; filename={ZIP_FILE_NAME.format(user_uuid)}",
            "Content-Encoding": "deflate"
        }

    return answer


def generate_zip_file():
    logger.info("start generating zip file")
    zf = zipfile.ZipFile("/tmp/" + ZIP_FILE_NAME.format(user_uuid), "w")
    for dirname, subdirs, files in os.walk(CONFIG_DIR_TEMPLATE):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

    logger.info("zip for user {} generated".format(user_uuid))


def lambda_handler(event, context):
    global user_uuid
    request_body = event["body"]
    user_uuid = request_body["uuid"]
    thing_name = request_body["thing_name"]

    answer = {}
    if user_uuid is None or thing_name is None:
        answer["statusCode"] = 500
        answer["message"] = "uuid or thing name not provided"
    else:
        answer = provision_device(thing_name)

    return answer

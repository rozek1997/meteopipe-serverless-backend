import json
import logging
import os
import zipfile

import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
DEVICE_TABLE_NAME = os.environ.get("DEVICE_TABLE")
topic = "meteopipe-thing/{uuid}/{ThingName}"

iot_client = boto3.client("iot")
# dynamo_client = boto3.client("dynamodb")
dynamodb = boto3.resource("dynamodb")
DEVICE_TABLE = dynamodb.Table(DEVICE_TABLE_NAME)
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

CA_CERT_URL = [
    'https://www.amazontrust.com/repository/AmazonRootCA1.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA2.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA3.pem',
    'https://www.amazontrust.com/repository/AmazonRootCA4.pem',
    'https://www.amazontrust.com/repository/SFSRootCAG2.pem'
]
CONFIG_DIR_TEMPLATE = "/tmp/{}/"
POLICY_NAME_TEMPLATE = "meteopipe-user-policy-{}"
PUBLIC_KEY_FILE_TEMPLATE = "{}.public.key"
PRIVATE_KEY_FILE_TEMPLATE = "{}.private.key"
CERT_PEM_FILE_TEMPLATE = "{}.cert.pem"
CA_CERT_FILE_NAME = "root.ca.bundle.pem"
CONFIG_FILE_NAME = "config.json"
ZIP_FILE_NAME = "{}-meteopipe.zip"
S3_BUCKET_NAME = "meteopipe-app"
S3_CERT_FOLDER = "users_cert/"
user_uuid = "{}-meteopipe.zip"


def thing_can_be_provision(thing_name):
    try:
        response_iot = iot_client.describe_thing(
            thingName=thing_name
        )
        response_database = DEVICE_TABLE.get_item(
            Key={
                "deviceID": thing_name,
                "uuid-prefix": user_uuid
            }
        )
        if "Item" in response_database or response_iot is not None:
            raise Exception("Device exist in database")
    except iot_client.exceptions.ResourceNotFoundException:
        logger.info("thing {} not found. Can be provisioned".format(thing_name))


def create_thing(thing_name: str):
    thing = iot_client.create_thing(thingName=thing_name)
    return thing


def put_thing_to_database():
    pass


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


def define_config_json(thing_name: str, endpoint: str):
    config = {
        "clientId": thing_name,
        "endpoints": endpoint,
        "topic": topic.format(uuid=user_uuid, ThingName=thing_name),
        "public_key_path": "",
        "private_key_path": "",
        "cert_path": "",
        "ca_cert_path": ""

    }

    return json.dumps(config, indent=4)  # intend make json look pretty, it like prettify


def generate_config_file(config: str):
    config_file_name = CONFIG_DIR_TEMPLATE + CONFIG_FILE_NAME
    os.chdir(CONFIG_DIR_TEMPLATE)
    configuration_json = json.dumps(config)
    with open(config_file_name, "w") as CONFIG_FILE:
        CONFIG_FILE.write(configuration_json)

    CONFIG_FILE.close()


def define_thing_endpoint():
    endpoint = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]
    return endpoint


def generate_zip_file():
    logger.info("start generating zip file")
    zip_name = ZIP_FILE_NAME.format(user_uuid)
    generated_zip_path = "/tmp/" + zip_name
    zf = zipfile.ZipFile(generated_zip_path, "w")
    for dirname, subdirs, files in os.walk(CONFIG_DIR_TEMPLATE):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

    logger.info("zip for user {} generated".format(user_uuid))

    return generated_zip_path, zip_name


def upload_zip_to_s3(zip_path: str, zip_name: str):
    logger.info("Uploading zip file to s3")
    s3_resource.meta.client.upload_file(zip_path, S3_BUCKET_NAME, S3_CERT_FOLDER + zip_name)
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": S3_CERT_FOLDER + zip_name
        },
        ExpiresIn=600
    )

    logger.info("Url for zip generated: {}".format(url))
    return url


def provision_device(thing_name: str):
    answer = {}
    logger.info("thing_name: {}, uuid: {}".format(thing_name, user_uuid))

    thing_complete_name = user_uuid + "-" + thing_name  # thing name with user id prefix
    # section of provisioning device
    try:
        thing_can_be_provision(thing_complete_name)
        thing = create_thing(thing_complete_name)
        attach_thing_to_thing_group(thing)
        cert_and_keys = generate_device_cert()
        attach_policy_to_cert(cert_and_keys["certificateArn"])
    except Exception as error:
        logger.error("Cant create thing with thing name {}, error message {}".format(thing_name, error))
        answer["statusCode"] = 400
        answer["message"] = str(error)
    else:  # section of preparing answer
        logger.info("creating {} user files for thing {}".format(user_uuid, thing_name))
        create_user_config_dir()
        generate_ca_cert()
        generate_cert_and_key_files(cert_and_keys)
        endpoint_address = define_thing_endpoint()
        config_template = define_config_json(thing_complete_name, endpoint_address)
        generate_config_file(config_template)
        zip_path, zip_name = generate_zip_file()
        get_cert_url = upload_zip_to_s3(zip_path, zip_name)

        answer["statusCode"] = 200
        answer["headers"] = {
            'Content-Type': 'application/json'
        }
        answer["body"] = json.dumps({"get_file_url": get_cert_url})

    return answer


def lambda_handler(event, context):
    global user_uuid
    logger.info(type(event["body"]))
    request_body = json.loads(event["body"])
    user_uuid = request_body["uuid"]
    thing_name = request_body["thing_name"]

    answer = {}
    if user_uuid is None or thing_name is None:
        answer["statusCode"] = 400
        answer["message"] = "uuid or thing name not provided"
    else:
        answer = provision_device(thing_name)

    logger.info(answer)
    return answer

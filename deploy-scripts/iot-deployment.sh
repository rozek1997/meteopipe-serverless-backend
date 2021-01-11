#!/bin/bash

mkdir "build"

sam package --template ./meteo_pipe/iot/iot-template.yaml --s3-bucket meteopipe-app --s3-prefix iot-setting \
  --region eu-central-1 --output-template-file ./build/iot-template-out.yaml

sam deploy --template-file ./build/iot-template-out.yaml \
  --stack-name iot-meteo-pipe --capabilities CAPABILITY_NAMED_IAM

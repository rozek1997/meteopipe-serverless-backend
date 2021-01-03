#!/bin/bash

mkdir "build"

sam package --template ./meteo_pipe/api/api-template.yaml --s3-bucket meteopipe-app --s3-prefix api-setting \
  --region eu-central-1 --output-template-file ./build/api-template-out.yaml

sam deploy --template-file ./build/api-template-out.yaml \
  --stack-name api-meteo-pipe --capabilities CAPABILITY_NAMED_IAM

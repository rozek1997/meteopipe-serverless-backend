#!/bin/bash

mkdir "build"

sam package --template ./meteo_pipe/auth/auth-template.yaml --s3-bucket meteopipe-app --s3-prefix auth-setting \
  --region eu-central-1 --output-template-file ./build/auth-template-out.yaml

sam deploy --template-file ./build/auth-template-out.yaml \
  --stack-name auth-meteo-pipe --capabilities CAPABILITY_NAMED_IAM

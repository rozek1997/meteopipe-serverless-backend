#!/bin/bash

mkdir "build"

rm -rf ./dependencies/python

pip3 install --target ./dependencies/python -r ./dependencies/requirements.txt

sam package --template ./root-template.yaml --s3-bucket meteopipe-app --s3-prefix root-setting \
  --region eu-central-1 --output-template-file ./build/root-template-out.yaml

sam deploy --template-file ./build/root-template-out.yaml \
  --stack-name meteo-pipe --capabilities CAPABILITY_NAMED_IAM

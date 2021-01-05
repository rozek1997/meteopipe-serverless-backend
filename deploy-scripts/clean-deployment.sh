#!/bin/bash

aws cloudformation delete-stack --stack-name "auth-meteo-pipe"
aws cloudformation delete-stack --stack-name "api-meteo-pipe"
sleep 10
aws cloudformation delete-stack --stack-name "meteo-pipe"

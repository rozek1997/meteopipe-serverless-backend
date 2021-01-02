#!/bin/bash

aws cloudformation delete-stack --stack-name "auth-meteo-pipe"
sleep 5
aws cloudformation delete-stack --stack-name "meteo-pipe"

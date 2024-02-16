#!/bin/bash

docker build -t deco-app .
#--build-arg APP_HOME="/app"
docker run -p 5001:5001 deco-app


#docker container rm $(docker container ls -a -q)

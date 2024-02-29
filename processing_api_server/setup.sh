#!/bin/sh

Dockerfile_folders="airlines_api airlines_ml"

for i in $Dockerfile_folders
  do
    docker image build $i -t $i:latest
  done

docker-compose up -d

crontab -l | { cat; echo "18 */1 * * * docker-compose -f $PWD/docker-compose.yml up airlines_ml"; } | crontab -

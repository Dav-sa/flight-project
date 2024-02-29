#!/usr/bin/env bash

Dockerfile_folders="airlines_api airlines_ml"

for i in $Dockerfile_folders
  do
    docker image build $i -t $i:latest
  done

docker compose up -d
docker run --rm --volume $PWD/shared:/home/shared -d airlines_ml python3 /home/shared/train_ml.py
crontab -l | { cat; echo "18 */1 * * * docker run --rm --volume $PWD/shared:/home/shared -d airlines_ml python3 /home/shared/train_ml.py"; } | crontab -

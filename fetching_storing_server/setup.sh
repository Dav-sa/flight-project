#!/usr/bin/env bash

docker image build mongo_dump -t mongo_dump:latest

docker-compose up -d

sleep 60

docker run --rm --volume $PWD/shared:/home/shared -d mongo_dump
crontab -l | { cat; echo "09 */1 * * * docker run --rm --volume $PWD/shared:/home/shared -d mongo_dump"; } | crontab -

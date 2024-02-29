#!/usr/bin/env bash

docker image build mongo_dump -t mongo_dump:latest

docker-compose up -d

crontab -l | { cat; echo "09 */1 * * * docker-compose -f $PWD/docker-compose.yml up mongo_dump"; } | crontab -

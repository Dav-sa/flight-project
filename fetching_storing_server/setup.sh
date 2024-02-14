#!/usr/bin/env bash

pip install requirements.txt

docker compose up -d

crontab -l | { cat; echo "09 */1 * * * python3 $PWD/mongo_dump.py"; } | crontab -

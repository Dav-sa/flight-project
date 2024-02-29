FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3-pip python3-dotenv && pip3 install pymongo==4.6.1 requests
WORKDIR /home/shared/
CMD python3 mongo_dump.py

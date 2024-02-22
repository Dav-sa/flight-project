FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3-pip openjdk-8-jdk-headless uvicorn python3-dotenv && pip3 install pyspark==3.2.4 pandas geopandas contextily numpy fastapi uvloop httptools==0.1.*
WORKDIR /home/shared/
CMD uvicorn main:api --reload --host 0.0.0.0

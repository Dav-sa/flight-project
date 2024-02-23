FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3-pip openjdk-8-jdk-headless python3-dotenv && pip3 install pyspark==3.2.4 numpy
WORKDIR /home/shared/
CMD python3 train_ml.py

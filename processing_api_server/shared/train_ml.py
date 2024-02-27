from dotenv import load_dotenv
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexerModel, StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline

load_dotenv()
uri = os.environ.get("MONGODB_URI")

spark = SparkSession.builder.appName("airlines_ml") \
    .config("spark.mongodb.read.connection.uri", uri) \
    .config("spark.mongodb.write.connection.uri", uri) \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:10.2.1') \
    .getOrCreate()

pipeline = "[{'$match':{'status':'active'}},{'$project' : {'dep_icao':1, 'arr_icao':1, 'duration':1, 'dep_delayed':1, 'flight_rules':1, 'wind_speed':1}}]"
df = spark.read \
    .format("mongodb") \
    .option("database", "airlines") \
    .option("collection", "airfrance") \
    .option("aggregation.pipeline", pipeline) \
    .load()

df_train = df.select(df.dep_delayed, df.dep_icao, df.arr_icao, df.duration, df.flight_rules, df.wind_speed)
df_train = df_train.withColumnRenamed("dep_delayed", "label").fillna(0, "label").dropna()

rulesIndexer = StringIndexerModel.from_labels(["VFR","MVFR","IFR","LIFR"], inputCol="flight_rules", outputCol="flight_rules_indexed")
nameIndexer = StringIndexer(inputCols=["dep_icao","arr_icao"], outputCols=["dep_icao_indexed","arr_icao_indexed"])
ohe = OneHotEncoder(inputCols=["dep_icao_indexed","arr_icao_indexed"], outputCols=["dep_icao_ohe","arr_icao_ohe"])
assembler = VectorAssembler(inputCols=["duration","dep_icao_ohe","arr_icao_ohe","flight_rules_indexed","wind_speed"], outputCol="features")
rf = RandomForestRegressor(labelCol="label", featuresCol="features")

pipeline = Pipeline(stages=[rulesIndexer, nameIndexer, ohe, assembler, rf])

model = pipeline.fit(df_train).write().overwrite().save("rf_model")

from dotenv import load_dotenv
import os
from pyspark.sql import SparkSession
import json

load_dotenv()
uri = os.environ.get("MONGODB_URI")

spark = SparkSession.builder.appName("airlines") \
    .config("spark.mongodb.read.connection.uri", uri) \
    .config("spark.mongodb.write.connection.uri", uri) \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:10.2.1') \
    .getOrCreate()

pipeline = "[{'$project' : {'flight_icao':1, 'airline_icao':1, 'dep_icao':1, 'arr_icao':1, 'duration':1, 'dep_delayed':1, 'flight_rules':1, 'wind_speed':1}}]"

df = spark.read \
    .format("mongodb") \
    .option("database", "airlines") \
    .option("collection", "airfrance") \
    .option("aggregation.pipeline", pipeline) \
    .load()

# STATS PROCESSING

df.printSchema()
df.show(20)
rdd = df.rdd

airports_delay = dict(rdd.map(lambda x: (x.dep_icao, ((0 if x.dep_delayed==None else x.dep_delayed), 1))) \
    .reduceByKey(lambda tuple1,tuple2: tuple(map(lambda x, y: x + y, tuple1, tuple2))) \
    .map(lambda x: (x[0],  round(x[1][0]/x[1][1], 2)) ) \
    .sortBy(lambda x: x[1], ascending = False) \
    .collect())

print(json.dumps(airports_delay))


delayed_sum = rdd.map(lambda x: x.dep_delayed).filter(lambda x: x!=None).sum()
print("Retard moyen d'airfrance: %.2f" %(delayed_sum/rdd.count()))

# ML PROCESSING

df_ml = df.select(df.dep_delayed, df.dep_icao, df.arr_icao, df.duration, df.flight_rules, df.wind_speed)
df_ml = df_ml.fillna(0, "dep_delayed").dropna()

from pyspark.ml.feature import StringIndexerModel
rulesIndexer = StringIndexerModel.from_labels(["VFR","MVFR","IFR","LIFR"], inputCol="flight_rules", outputCol="flight_rules_indexed")
df_ml = rulesIndexer.transform(df_ml)

from pyspark.ml.feature import StringIndexer
nameIndexer = StringIndexer(inputCols=["dep_icao","arr_icao"], outputCols=["dep_icao_indexed","arr_icao_indexed"])
df_ml = nameIndexer.fit(df_ml).transform(df_ml)

from pyspark.ml.feature import OneHotEncoder
ohe = OneHotEncoder(inputCols=["dep_icao_indexed","arr_icao_indexed"], outputCols=["dep_icao_ohe","arr_icao_ohe"],)
df_ml = ohe.fit(df_ml).transform(df_ml)

from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(inputCols=["duration", "dep_icao_ohe", "arr_icao_ohe", "flight_rules_indexed", "wind_speed"],outputCol="features")
df_ml = assembler.transform(df_ml).select("dep_delayed", "features").withColumnRenamed("dep_delayed", "label")

train, test = df_ml.randomSplit([.8, .2], seed=99)

from pyspark.ml.regression import LinearRegression
lr = LinearRegression(labelCol='label', featuresCol='features')
linearModel = lr.fit(train)
lrpredicted = linearModel.transform(test)
lrpredicted.show()
print("RMSE:", linearModel.summary.rootMeanSquaredError)
print("R2:  ", linearModel.summary.r2)

from pyspark.ml.regression import RandomForestRegressor
rf = RandomForestRegressor(labelCol = "label",featuresCol = 'features')
rfModel = rf.fit(train)
rfpredicted = rfModel.transform(test)
rfpredicted.show()

from pyspark.ml.evaluation import RegressionEvaluator
eval = RegressionEvaluator(labelCol = 'label')
rmse = eval.evaluate(rfpredicted, {eval.metricName:'rmse'})
r2 = eval.evaluate(rfpredicted,{eval.metricName:'r2'})
print("RMSE: %.2f" %rmse)
print("R2: %.2f" %r2)

###

spark.stop()

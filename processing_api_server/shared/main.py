from dotenv import load_dotenv
import os
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pyspark.sql import SparkSession
import json
import pandas as pd
import geopandas as gpd
import contextily as cx
import requests
import matplotlib.pyplot as plt
from pyspark.ml.feature import StringIndexerModel, StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor

api = FastAPI(
	title="Airlines_API",
	description="API Airlines",
	version="1.0")

load_dotenv()
uri = os.environ.get("MONGODB_URI")
airlabs_api_key = os.environ.get("AIRLABS_KEY")

spark = SparkSession.builder.appName("airlines") \
    .config("spark.mongodb.read.connection.uri", uri) \
    .config("spark.mongodb.write.connection.uri", uri) \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:10.2.1') \
    .getOrCreate()

def spark_read():
	spark = SparkSession.builder.getOrCreate()
	pipeline = "[{'$project' : {'flight_icao':1, 'airline_icao':1, 'dep_icao':1, 'arr_icao':1, 'duration':1, 'dep_delayed':1, 'flight_rules':1, 'wind_speed':1}}]"
	df = spark.read \
	        .format("mongodb") \
	        .option("database", "airlines") \
	        .option("collection", "airfrance") \
	        .option("aggregation.pipeline", pipeline) \
	        .load()
	return(df)

###

@api.get('/airports_delay')
async def get_airports_delay():
    """Returns airports delay
    """
    rdd = spark_read().rdd
    airports_delay = dict(rdd.map(lambda x: (x.dep_icao, ((0 if x.dep_delayed==None else x.dep_delayed), 1))) \
        .reduceByKey(lambda tuple1,tuple2: tuple(map(lambda x, y: x + y, tuple1, tuple2))) \
        .map(lambda x: (x[0],  round(x[1][0]/x[1][1], 2)) ) \
        .sortBy(lambda x: x[1], ascending = False) \
        .collect())
    return Response(content=json.dumps(airports_delay), media_type="application/json")

@api.get('/mean_delay')
async def get_mean_delay():
    """Returns mean delay
    """
    rdd = spark_read().rdd
    delayed_sum = rdd.map(lambda x: x.dep_delayed).filter(lambda x: x!=None).sum()
    return {
        "Retard moyen d'airfrance": round(delayed_sum/rdd.count(),2)
        }

@api.get("/flights_map")
def get_flights_map():
    """Returns a flight map as a png
    """
    params = {"api_key": airlabs_api_key}
    flights_result = requests.get("https://airlabs.co/api/v9/flights", params)
    df = pd.DataFrame(flights_result.json()["response"])
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.lng, df.lat)).drop(['lng',"lat"], axis=1).set_crs('epsg:4326')
    ax = gdf.to_crs(epsg=3857).plot(figsize=(50,50),alpha=0.5)
    cx.add_basemap(ax)
    plt.savefig('flights_map.png', bbox_inches='tight')
    return FileResponse("flights_map.png", media_type="image/png")

class Item(BaseModel):
	dep_icao: str
	arr_icao: str
	duration: int
	flight_rules: str
	wind_speed: int

@api.post('/ml_prediction')
async def ml_prediction(item: Item):
    df = spark_read()
    df_ml = df.select(df.dep_delayed, df.dep_icao, df.arr_icao, df.duration, df.flight_rules, df.wind_speed)
    df_ml = df_ml.withColumnRenamed("dep_delayed", "label").fillna(0, "label").dropna()
    df_input = spark.createDataFrame([(item.dep_icao, item.arr_icao, item.duration, item.flight_rules, item.wind_speed)],["dep_icao", "arr_icao", "duration", "flight_rules", "wind_speed"])

    rulesIndexer = StringIndexerModel.from_labels(["VFR","MVFR","IFR","LIFR"], inputCol="flight_rules", outputCol="flight_rules_indexed")
    df_ml = rulesIndexer.transform(df_ml)
    df_input = rulesIndexer.transform(df_input)

    nameIndexer = StringIndexer(inputCols=["dep_icao","arr_icao"], outputCols=["dep_icao_indexed","arr_icao_indexed"]).fit(df_ml)
    df_ml = nameIndexer.transform(df_ml)
    df_input = nameIndexer.transform(df_input)

    ohe = OneHotEncoder(inputCols=["dep_icao_indexed","arr_icao_indexed"], outputCols=["dep_icao_ohe","arr_icao_ohe"]).fit(df_ml)
    df_ml = ohe.transform(df_ml)
    df_input = ohe.transform(df_input)

    assembler = VectorAssembler(inputCols=["duration", "dep_icao_ohe", "arr_icao_ohe", "flight_rules_indexed", "wind_speed"],outputCol="features")
    df_ml = assembler.transform(df_ml)
    df_input = assembler.transform(df_input)

    rf = RandomForestRegressor(labelCol = "label",featuresCol = 'features')
    rfModel = rf.fit(df_ml)
    rfpredicted = rfModel.transform(df_input).collect()[0][-1]

    return {
        "Random Forest prediction": round(rfpredicted, 2),
        }

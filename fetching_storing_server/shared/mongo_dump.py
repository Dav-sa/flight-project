from dotenv import load_dotenv
import os
import requests
import json
from pymongo import MongoClient
from pymongo import UpdateOne
from pprint import pprint

load_dotenv()
airlabs_api_key = os.environ.get("AIRLABS_KEY")
avwx_api_key = os.environ.get("AVWX_KEY")
uri = os.environ.get("MONGODB_URI_LOCAL")

# Fetch airlabs flights
params = {"api_key": airlabs_api_key, "airline_icao":"AFR"}
api_result = requests.get("https://airlabs.co/api/v9/schedules", params)

api_response = api_result.json()["response"]

# Fetch flights departure airport weather condition
Airports_weather = {}
for x in api_response:
    try:
        dep_icao = x["dep_icao"]
        if dep_icao!=None and dep_icao not in Airports_weather.keys():
            weather_result = requests.get("https://avwx.rest/api/metar/" + dep_icao , headers={"Authorization":"BEARER " + avwx_api_key}).json()
            try:
                flight_rules = weather_result["flight_rules"]
            except:
                flight_rules = None
            try:
                wind_speed = weather_result["wind_speed"]["value"]
            except:
                wind_speed = None
            Airports_weather[dep_icao] = [flight_rules, wind_speed]
    except Exception as e:
        print(x["dep_icao"])
        Airports_weather[x["dep_icao"]] = [None, None]
        print(e)

client = MongoClient(uri)

# Send a ping to confirm a successful connection to MongoDB server
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Store data to MongoDB
db = client["airlines"]
collection = db["airfrance"]

BulkArr = []
for x in api_response:
    if x["status"] != "active":
        BulkArr.append(UpdateOne(
        {"flight_icao": x["flight_icao"], "flight_number": x["flight_number"], "status": x["status"]},
        {'$set': x}, upsert=True))
    else:
        airport_weather = Airports_weather[x["dep_icao"]]
        BulkArr.append(UpdateOne(
        {"flight_icao": x["flight_icao"], "flight_number": x["flight_number"], "status": x["status"]},
        {'$set': x, '$setOnInsert': {"flight_rules": airport_weather[0], "wind_speed": airport_weather[1]}}, upsert=True))

try :
    result = collection.bulk_write( BulkArr )
    pprint(result.bulk_api_result)
except Exception as e:
    print(e)

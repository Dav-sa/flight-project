import pymongo
import json
from pymongo.errors import ConnectionFailure

# Read the JSON file
with open("flights.json") as file:
    data = json.load(file)


# Establish a connection to the local MongoDB instance
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/meteor?ssl=false")

# Select the database
db = client["meteor"]

# Select the collection
collection = db["real time flights"]

# Insert the JSON data into the collection
collection.insert_one(data)

try:
    # Check if the server is available using the ping command
    client.admin.command("ping")
    print("Server is available")
except ConnectionFailure:
    print("Server not available")

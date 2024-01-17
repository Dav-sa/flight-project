from dotenv import load_dotenv
import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Read the JSON file
with open("flights.json") as file:
    data = json.load(file)

load_dotenv()
uri = os.environ.get("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Select the database
db = client["meteor"]

# Select the collection
collection = db["real time flights"]

# Insert the JSON data into the collection
collection.insert_many(data)

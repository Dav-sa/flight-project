from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from pymongo.errors import ConnectionFailure
import dns.resolver

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


uri = 'mongodb+srv://david:ml&é"ùZE!!@flight-project.iospxhv.mongodb.net/?retryWrites=true&w=majority'


client = MongoClient(uri, server_api=ServerApi("1"))
db = client["airfrance"]
collection = db["airfrance_flights"]

try:
    client.admin.command("ping")
    print("Server is available")
except ConnectionFailure:
    print("Server not available")

with open("./results/flights.json") as f:
    data = json.load(f)
    collection.insert_one(data)

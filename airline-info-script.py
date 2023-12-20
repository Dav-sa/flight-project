from dotenv import load_dotenv
import os
import requests


load_dotenv()
api_key = os.environ.get("API_KEY")

params = {"access_key": api_key}

api_result = requests.get("http://api.aviationstack.com/v1/airlines", params)

api_response = api_result.json()

air_france_general_data = api_response["data"][17]

print(air_france_general_data)

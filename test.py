import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY")

url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 50
}

response = requests.get(url, params=params)

data = response.json()

for r in data["records"]:
    print(r)
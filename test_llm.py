import requests
import os
from dotenv import load_dotenv
load_dotenv()

r = requests.post(
    "https://api.sarvam.ai/v1/chat/completions",
    headers={
        "api-subscription-key": os.getenv("SARVAM_API_KEY"),
        "Content-Type": "application/json"
    },
    json={
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": "say hi"}],
        "temperature": 0
    },
    timeout=120
)
print("Status:", r.status_code)
print("Response:", r.text[:500])
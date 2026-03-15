"""
test_translate.py — Test Sarvam Translate for Hindi commodity names
Run: python test_translate.py
"""

import requests
import os
from dotenv import load_dotenv
load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TRANSLATE_URL  = "https://api.sarvam.ai/translate"

def translate(text: str) -> str:
    resp = requests.post(
        TRANSLATE_URL,
        headers={"api-subscription-key": SARVAM_API_KEY},
        json={
            "input":           text,
            "source_language_code": "hi-IN",
            "target_language_code": "en-IN",
            "model":           "mayura:v1",
            "mode":            "formal"
        },
        timeout=15
    )
    result = resp.json()
    print(f"Raw response: {result}")
    return result.get("translated_text", "")

# Test common commodity names
test_commodities = [
    "टमाटर", "आलू", "प्याज", "गाजर", "पालक",
    "भिंडी", "बैंगन", "मटर", "सरसों", "गेहूं"
]

print("Testing Sarvam Translate for commodity names...\n")
for commodity in test_commodities:
    translated = translate(commodity)
    print(f"  {commodity:<15} → {translated}")
    print()
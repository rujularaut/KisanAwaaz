"""
services/llm_service.py — Entity extraction using Sarvam AI
"""

import re
import json
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
LLM_URL = "https://api.sarvam.ai/v1/chat/completions"


def extract_entities(transcript: str) -> dict:
    if not transcript or not transcript.strip():
        return {"commodity": "", "market": "", "state": ""}

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    prompt = f"""
Extract the following fields from the farmer query.

Return ONLY valid JSON. No explanation. No markdown.

Fields:
- commodity  (crop/vegetable name in Hindi)
- market     (mandi name in Hindi)
- state      (Indian state name)

If a field is not mentioned, return empty string "".

Farmer query:
{transcript}

Output format:
{{
  "commodity": "",
  "market": "",
  "state": ""
}}
"""

    payload = {
        "model": "sarvam-105b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        response = requests.post(LLM_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        logger.debug("LLM raw response: %s", result)
        print("LLM raw response:", result)
    except Exception as e:
        logger.error("Sarvam API call failed: %s", e)
        return {"commodity": "", "market": "", "state": ""}

    if "choices" not in result:
        logger.error("Unexpected API response: %s", result)
        return {"commodity": "", "market": "", "state": ""}

    content = result["choices"][0]["message"]["content"].strip()
    content = re.sub(r"```(?:json)?", "", content).replace("```", "").strip()

    json_match = re.search(r"\{.*?\}", content, re.DOTALL)
    if not json_match:
        logger.error("No JSON found in LLM content: %s", content)
        return {"commodity": "", "market": "", "state": ""}

    try:
        entities = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s | content: %s", e, content)
        return {"commodity": "", "market": "", "state": ""}

    return {
        "commodity": str(entities.get("commodity") or "").strip(),
        "market":    str(entities.get("market")    or "").strip(),
        "state":     str(entities.get("state")     or "").strip(),
    }


def extract_query_entities(transcript: str) -> dict:
    return extract_entities(transcript)
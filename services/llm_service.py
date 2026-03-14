"""
services/llm_service.py — Entity extraction using Sarvam AI (sarvam-m)
sarvam-m is faster and more reliable than sarvam-105b for this task.
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

MAX_RETRIES = 2
TIMEOUT     = 30


def extract_entities(transcript: str) -> dict:
    """
    Extract commodity, market, state from a Hindi farmer query.
    Returns a clean dict always.
    """
    if not transcript or not transcript.strip():
        return {"commodity": "", "market": "", "state": ""}

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    prompt = f"""Extract the following fields from the farmer query.

Return ONLY valid JSON. No explanation. No markdown. No <think> tags.

Fields:
- commodity  (crop/vegetable name in Hindi)
- market     (mandi name in Hindi)
- state      (Indian state name)

If a field is not mentioned, return empty string "".

Examples:
Input: "बड़वानी मंडी में टमाटर का भाव क्या है?"
Output: {{"commodity": "टमाटर", "market": "बड़वानी", "state": ""}}

Input: "गुजरात में सूरत मंडी में आलू का दाम बताओ"
Output: {{"commodity": "आलू", "market": "सूरत", "state": "गुजरात"}}

Farmer query: {transcript}

Output:"""

    payload = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔄  LLM attempt {attempt}/{MAX_RETRIES} …")
            response = requests.post(
                LLM_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json()

            if "choices" not in result:
                print(f"⚠️  Unexpected response: {result}")
                continue

            content = result["choices"][0]["message"]["content"].strip()

            # Strip <think>...</think> tags if model includes reasoning
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            # Strip markdown fences
            content = re.sub(r"```(?:json)?", "", content).replace("```", "").strip()

            print(f"📝  LLM content: {content}")

            json_match = re.search(r"\{.*?\}", content, re.DOTALL)
            if not json_match:
                print(f"⚠️  No JSON found in: {content}")
                continue

            entities = json.loads(json_match.group())
            result_dict = {
                "commodity": str(entities.get("commodity") or "").strip(),
                "market":    str(entities.get("market")    or "").strip(),
                "state":     str(entities.get("state")     or "").strip(),
            }
            print(f"✅  LLM succeeded on attempt {attempt}")
            return result_dict

        except requests.exceptions.Timeout:
            print(f"⏱️  Attempt {attempt} timed out after {TIMEOUT}s")
        except Exception as e:
            print(f"❌  Attempt {attempt} failed: {e}")

    print("❌  All LLM attempts failed. Returning empty entities.")
    return {"commodity": "", "market": "", "state": ""}


def extract_query_entities(transcript: str) -> dict:
    return extract_entities(transcript)
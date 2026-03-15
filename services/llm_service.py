"""
services/llm_service.py — Simulated MCP with Sarvam-m
Fixed: empty response fallback + cleaner response generation
"""

import re
import json
import logging
import requests
import os
from dotenv import load_dotenv
from mcp_server import TOOLS_DESCRIPTION, execute_tool

load_dotenv()

logger         = logging.getLogger(__name__)
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
LLM_URL        = "https://api.sarvam.ai/v1/chat/completions"
TIMEOUT        = 30
MAX_RETRIES    = 2

# Hindi number words for price generation fallback
HINDI_NUMBERS = {
    0: "शून्य", 1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पाँच",
    6: "छह", 7: "सात", 8: "आठ", 9: "नौ", 10: "दस",
    11: "ग्यारह", 12: "बारह", 13: "तेरह", 14: "चौदह", 15: "पंद्रह",
    16: "सोलह", 17: "सत्रह", 18: "अठारह", 19: "उन्नीस", 20: "बीस",
    21: "इक्कीस", 22: "बाईस", 23: "तेईस", 24: "चौबीस", 25: "पच्चीस",
    26: "छब्बीस", 27: "सत्ताईस", 28: "अट्ठाईस", 29: "उनतीस", 30: "तीस",
    31: "इकतीस", 32: "बत्तीस", 33: "तैंतीस", 34: "चौंतीस", 35: "पैंतीस",
    36: "छत्तीस", 37: "सैंतीस", 38: "अड़तीस", 39: "उनतालीस", 40: "चालीस",
    41: "इकतालीस", 42: "बयालीस", 43: "तैंतालीस", 44: "चवालीस", 45: "पैंतालीस",
    46: "छियालीस", 47: "सैंतालीस", 48: "अड़तालीस", 49: "उनचास", 50: "पचास",
    51: "इक्यावन", 52: "बावन", 53: "तिरपन", 54: "चौवन", 55: "पचपन",
    56: "छप्पन", 57: "सत्तावन", 58: "अट्ठावन", 59: "उनसठ", 60: "साठ",
    61: "इकसठ", 62: "बासठ", 63: "तिरसठ", 64: "चौंसठ", 65: "पैंसठ",
    66: "छियासठ", 67: "सड़सठ", 68: "अड़सठ", 69: "उनहत्तर", 70: "सत्तर",
    71: "इकहत्तर", 72: "बहत्तर", 73: "तिहत्तर", 74: "चौहत्तर", 75: "पचहत्तर",
    76: "छिहत्तर", 77: "सतहत्तर", 78: "अठहत्तर", 79: "उन्यासी", 80: "अस्सी",
    81: "इक्यासी", 82: "बयासी", 83: "तिरासी", 84: "चौरासी", 85: "पचासी",
    86: "छियासी", 87: "सत्तासी", 88: "अट्ठासी", 89: "नवासी", 90: "नब्बे",
    91: "इक्यानवे", 92: "बानवे", 93: "तिरानवे", 94: "चौरानवे", 95: "पचानवे",
    96: "छियानवे", 97: "सत्तानवे", 98: "अट्ठानवे", 99: "निन्यानवे",
}

HINDI_MONTHS = {
    "01": "जनवरी", "02": "फ़रवरी", "03": "मार्च",  "04": "अप्रैल",
    "05": "मई",    "06": "जून",    "07": "जुलाई",  "08": "अगस्त",
    "09": "सितंबर","10": "अक्टूबर","11": "नवंबर",  "12": "दिसंबर",
}


def _number_to_hindi(n: int) -> str:
    if n in HINDI_NUMBERS:
        return HINDI_NUMBERS[n]
    if n < 1000:
        hun, rest = divmod(n, 100)
        return HINDI_NUMBERS[hun] + " सौ" + (" " + _number_to_hindi(rest) if rest else "")
    if n < 100000:
        thou, rest = divmod(n, 1000)
        return _number_to_hindi(thou) + " हज़ार" + (" " + _number_to_hindi(rest) if rest else "")
    lakh, rest = divmod(n, 100000)
    return _number_to_hindi(lakh) + " लाख" + (" " + _number_to_hindi(rest) if rest else "")


def _build_fallback_response(tool_result: dict, hindi_commodity: str) -> str:
    """
    Build Hindi response directly from price data without LLM.
    Used as fallback when Sarvam-m returns empty response.
    """
    market = tool_result.get("market", "")
    price  = tool_result.get("modal_price", "")
    date   = tool_result.get("date", "")

    try:
        price_hindi = _number_to_hindi(int(float(price)))
    except Exception:
        price_hindi = str(price)

    date_text = ""
    if date and date != "unknown":
        try:
            if "/" in date:
                day, month, year = date.split("/")
            elif "-" in date:
                year, month, day = date.split("-")
            date_text = f" {_number_to_hindi(int(day))} {HINDI_MONTHS.get(month.zfill(2), month)} को"
        except Exception:
            pass

    commodity = hindi_commodity if hindi_commodity else tool_result.get("commodity", "")
    return f"{market} मंडी में{date_text} {commodity} का भाव लगभग {price_hindi} रुपये प्रति क्विंटल है।"


def _clean(text: str) -> str:
    """Strip <think> blocks and XML tags from final Hindi response."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*",          "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>",            "", text)
    return text.strip()


def _extract_json(text: str) -> dict | None:
    """Extract JSON from raw text — works even inside <think> tags."""
    try:
        json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"  JSON parse error: {e}")
    return None


def _call_sarvam(messages: list) -> str:
    """Call Sarvam-m and return raw content string."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp   = requests.post(
                LLM_URL,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type":         "application/json"
                },
                json={
                    "model":       "sarvam-m",
                    "messages":    messages,
                    "temperature": 0
                },
                timeout=TIMEOUT
            )
            result = resp.json()
            if "choices" not in result:
                print(f"  Unexpected response: {result}")
                continue
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            print(f"  Attempt {attempt} timed out")
        except Exception as e:
            print(f"❌  Attempt {attempt} error: {e}")
    return ""


def process_farmer_query(transcript: str) -> dict:
    """
    Simulated MCP pipeline:
    Step 1 — Sarvam-m decides which tool to call
    Step 2 — MCP server executes the tool
    Step 3 — Sarvam-m generates Hindi response
             (falls back to template if Sarvam returns empty)
    """

    # ── MCP Step 1: Tool selection ────────────────────────────────────────
    print("  MCP Step 1: Asking Sarvam-m which tool to call …")

    tool_selection_prompt = f"""{TOOLS_DESCRIPTION}

Farmer query: {transcript}

Respond with ONLY the JSON tool call. No explanation. No extra text."""

    raw_tool_response = _call_sarvam([
        {"role": "user", "content": tool_selection_prompt}
    ])

    print(f"  Raw tool response: {raw_tool_response[:300]}")

    # ── Parse tool call ───────────────────────────────────────────────────
    tool_call = _extract_json(raw_tool_response)
    tool_name = tool_call.get("tool") if tool_call else None
    print(f"  MCP Step 2: Tool chosen → {tool_name} | Args: {tool_call}")

    # ── MCP Step 3: Execute tool ──────────────────────────────────────────
    tool_result = {}

    if tool_name in ("get_mandi_price", "get_best_mandi"):
        print(f"   MCP Step 3: Executing tool …")
        tool_result = execute_tool(tool_name, tool_call)
    else:
        print(f"  No valid tool selected")
        return {
            "response_text": "कृपया फसल और मंडी का नाम बताएं।",
            "mandi_data":    {},
            "tool_called":   None
        }

    # ── MCP Step 4: Generate Hindi response ───────────────────────────────
    print("  MCP Step 4: Generating Hindi response …")

    hindi_commodity = tool_call.get("commodity", "")

    if "error" in tool_result:
        response_text = f"माफ कीजिए, {hindi_commodity or 'इस फसल'} का भाव अभी उपलब्ध नहीं है।"
    else:
        response_prompt = f"""You are KisanAwaaz, a voice assistant for Indian farmers.
A farmer asked: "{transcript}"

Mandi price data:
- Market: {tool_result.get('market')}
- Modal Price: ₹{tool_result.get('modal_price')} per quintal
- Date: {tool_result.get('date')}

Reply in ONE short Hindi sentence with the price.
Use "{hindi_commodity}" as the crop name.
Format: "[Market] मंडी में [crop] का भाव लगभग [price in Hindi words] रुपये प्रति क्विंटल है।"
No English. No extra text."""

        raw_response  = _call_sarvam([{"role": "user", "content": response_prompt}])
        response_text = _clean(raw_response)

        # ── Fallback: if LLM returns empty, build response directly ──────
        if not response_text:
            print("  Empty LLM response — using direct fallback response")
            response_text = _build_fallback_response(tool_result, hindi_commodity)

    print(f"✅  MCP Step 5: Final Hindi response → {response_text}")

    return {
        "response_text": response_text,
        "mandi_data":    tool_result,
        "tool_called":   tool_name
    }


# Backward compatible aliases
def extract_entities(transcript: str) -> dict:
    result = process_farmer_query(transcript)
    data   = result.get("mandi_data", {})
    return {
        "commodity": data.get("commodity", ""),
        "market":    data.get("market", ""),
        "state":     data.get("state", ""),
    }

def extract_query_entities(transcript: str) -> dict:
    return extract_entities(transcript)
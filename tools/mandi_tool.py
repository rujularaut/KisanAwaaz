"""
tools/mandi_tool.py — Fetch mandi prices from Agmarknet government API
Translates Hindi commodity/market/state names to English before querying.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# ── Hindi → English commodity map ────────────────────────────────────────────
COMMODITY_MAP = {
    # Vegetables
    "टमाटर": "Tomato",
    "आलू": "Potato",
    "प्याज": "Onion",
    "लहसुन": "Garlic",
    "अदरक": "Ginger",
    "गोभी": "Cauliflower",
    "फूलगोभी": "Cauliflower",
    "पत्तागोभी": "Cabbage",
    "बैंगन": "Brinjal",
    "भिंडी": "Bhindi(Ladies Finger)",
    "भिण्डी": "Bhindi(Ladies Finger)",
    "करेला": "Bitter Gourd",
    "लौकी": "Bottle Gourd",
    "तोरई": "Ridgeguard(Tori)",
    "मटर": "Peas",
    "मेथी": "Methi(Leaves)",
    "पालक": "Spinach",
    "धनिया": "Coriander(Leaves)",
    "मिर्च": "Green Chilli",
    "हरी मिर्च": "Green Chilli",
    "लाल मिर्च": "Dry Chillies",
    "मूली": "Raddish",
    "गाजर": "Carrot",
    "शिमला मिर्च": "Capsicum",
    "कद्दू": "Pumpkin",
    "परवल": "Pointed Gourd (Parval)",
    "कटहल": "Jack Fruit",

    # Fruits
    "केला": "Banana",
    "सेब": "Apple",
    "आम": "Mango",
    "अंगूर": "Grapes",
    "संतरा": "Mosambi(Sweet Lime)",
    "मौसमी": "Mosambi(Sweet Lime)",
    "पपीता": "Papaya",
    "अनार": "Pomegranate",
    "तरबूज": "Water Melon",
    "खरबूजा": "Musk Melon",
    "नींबू": "Lemon",
    "अमरूद": "Guava",
    "नाशपाती": "Pear",
    "अनानास": "Pineapple",
    "चीकू": "Sapota(Chiku)",
    "लीची": "Litchi",

    # Grains & Pulses
    "गेहूं": "Wheat",
    "चावल": "Rice",
    "धान": "Paddy(Dhan)",
    "मक्का": "Maize",
    "बाजरा": "Bajra(Pearl Millet/Cumbu)",
    "ज्वार": "Jowar(Sorghum)",
    "चना": "Gram",
    "मसूर": "Masur Dal",
    "मूंग": "Moong (Whole)",
    "उड़द": "Black Gram (Urd Beans)(Whole)",
    "अरहर": "Arhar (Tur/Red Gram)(Whole)",
    "सोयाबीन": "Soyabean",
    "सरसों": "Mustard",
    "मूंगफली": "Groundnut",

    # Others
    "कपास": "Cotton",
    "गन्ना": "Sugarcane",
    "हल्दी": "Turmeric",
    "जीरा": "Cumin Seed(Jeera)",
}

# ── Hindi → English state map ────────────────────────────────────────────────
STATE_MAP = {
    "मध्यप्रदेश": "Madhya Pradesh",
    "मध्य प्रदेश": "Madhya Pradesh",
    "उत्तरप्रदेश": "Uttar Pradesh",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "राजस्थान": "Rajasthan",
    "महाराष्ट्र": "Maharashtra",
    "गुजरात": "Gujarat",
    "पंजाब": "Punjab",
    "हरियाणा": "Haryana",
    "बिहार": "Bihar",
    "पश्चिम बंगाल": "West Bengal",
    "कर्नाटक": "Karnataka",
    "तमिलनाडु": "Tamil Nadu",
    "तेलंगाना": "Telangana",
    "आंध्रप्रदेश": "Andhra Pradesh",
    "आंध्र प्रदेश": "Andhra Pradesh",
    "केरल": "Kerala",
    "ओडिशा": "Odisha",
    "छत्तीसगढ़": "Chhattisgarh",
    "झारखंड": "Jharkhand",
    "असम": "Assam",
    "हिमाचल प्रदेश": "Himachal Pradesh",
    "उत्तराखंड": "Uttarakhand",
    "दिल्ली": "Delhi",
}


def normalize_inputs(commodity: str, market: str, state: str):
    """Translate Hindi names to English for the government API."""

    # Commodity: try Hindi map first, then capitalize as fallback
    commodity_en = COMMODITY_MAP.get(commodity.strip(), None)
    if not commodity_en:
        # Try partial match
        for hindi, english in COMMODITY_MAP.items():
            if hindi in commodity:
                commodity_en = english
                break
        if not commodity_en:
            commodity_en = commodity.strip().capitalize()

    # Market: strip मंडी/मण्डी suffix and capitalize
    market_en = market.strip()
    for suffix in ["मंडी", "मण्डी", " mandi", " Mandi"]:
        market_en = market_en.replace(suffix, "").strip()
    market_en = market_en.capitalize()

    # State: try Hindi map, else capitalize as-is
    state_en = STATE_MAP.get(state.strip(), state.strip().capitalize())

    print(f"🔄  Normalized → commodity: {commodity_en}, market: {market_en}, state: {state_en}")
    return commodity_en, market_en, state_en


def get_mandi_price(commodity: str, market: str, state: str) -> dict:
    """
    Fetch mandi price data from Agmarknet dataset.
    Falls back to first available record if exact market not found.
    """
    commodity_en, market_en, state_en = normalize_inputs(commodity, market, state)

    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "filters[commodity]": commodity_en,
        "limit": 20
    }

    # Add state filter if available
    if state_en:
        params["filters[state]"] = state_en

    try:
        response = requests.get(BASE_URL, params=params, timeout=90)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": "Failed to connect to mandi price API",
            "details": str(e)
        }

    records = data.get("records", [])

    if not records:
        # Retry without state filter
        params.pop("filters[state]", None)
        try:
            response = requests.get(BASE_URL, params=params, timeout=90)
            data = response.json()
            records = data.get("records", [])
        except Exception:
            pass

    if not records:
        return {
            "error": "No mandi data found for commodity",
            "commodity": commodity_en
        }

    # Try to match the requested market
    if market_en:
        for record in records:
            if market_en.lower() in record.get("market", "").lower():
                return _build_result(record)

    # Fallback: return first record
    return _build_result(records[0])


def _build_result(record: dict) -> dict:
    return {
        "commodity": record.get("commodity"),
        "market":    record.get("market"),
        "state":     record.get("state"),
        "min_price": record.get("min_price"),
        "max_price": record.get("max_price"),
        "modal_price": record.get("modal_price"),
    }
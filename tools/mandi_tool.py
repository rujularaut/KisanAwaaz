"""
tools/mandi_tool.py — Fetch mandi prices from Agmarknet government API
"""

import requests
import os
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# ── Hindi → English commodity map ────────────────────────────────────────────
COMMODITY_MAP = {
    "टमाटर": "Tomato", "आलू": "Potato", "प्याज": "Onion",
    "लहसुन": "Garlic", "अदरक": "Ginger", "गोभी": "Cauliflower",
    "फूलगोभी": "Cauliflower", "पत्तागोभी": "Cabbage", "बैंगन": "Brinjal",
    "भिंडी": "Bhindi(Ladies Finger)", "भिण्डी": "Bhindi(Ladies Finger)",
    "करेला": "Bitter Gourd", "लौकी": "Bottle Gourd", "तोरई": "Ridgeguard(Tori)",
    "मटर": "Peas", "मेथी": "Methi(Leaves)", "पालक": "Spinach",
    "धनिया": "Coriander(Leaves)", "मिर्च": "Green Chilli",
    "हरी मिर्च": "Green Chilli", "लाल मिर्च": "Dry Chillies",
    "मूली": "Raddish", "गाजर": "Carrot", "शिमला मिर्च": "Capsicum",
    "कद्दू": "Pumpkin", "परवल": "Pointed Gourd (Parval)", "कटहल": "Jack Fruit",
    "केला": "Banana", "सेब": "Apple", "आम": "Mango", "अंगूर": "Grapes",
    "संतरा": "Mosambi(Sweet Lime)", "मौसमी": "Mosambi(Sweet Lime)",
    "पपीता": "Papaya", "अनार": "Pomegranate", "तरबूज": "Water Melon",
    "खरबूजा": "Musk Melon", "नींबू": "Lemon", "अमरूद": "Guava",
    "नाशपाती": "Pear", "अनानास": "Pineapple", "चीकू": "Sapota(Chiku)",
    "लीची": "Litchi", "गेहूं": "Wheat", "चावल": "Rice",
    "धान": "Paddy(Dhan)", "मक्का": "Maize",
    "बाजरा": "Bajra(Pearl Millet/Cumbu)", "ज्वार": "Jowar(Sorghum)",
    "चना": "Gram", "मसूर": "Masur Dal", "मूंग": "Moong (Whole)",
    "उड़द": "Black Gram (Urd Beans)(Whole)",
    "अरहर": "Arhar (Tur/Red Gram)(Whole)", "सोयाबीन": "Soyabean",
    "सरसों": "Mustard", "मूंगफली": "Groundnut", "कपास": "Cotton",
    "गन्ना": "Sugarcane", "हल्दी": "Turmeric", "जीरा": "Cumin Seed(Jeera)",
}

# ── Hindi → EXACT English market name as in dataset ──────────────────────────
# Use check_markets.py to verify exact names for any new city
MARKET_MAP = {
    # Maharashtra (verified from dataset)
    "अलीबाग": "Alibagh APMC",
    "मुरुड": "Murud APMC",
    # Madhya Pradesh
    "इंदौर": "Indore",
    "भोपाल": "Bhopal",
    "बड़वानी": "Badwani",
    "ग्वालियर": "Gwalior",
    "जबलपुर": "Jabalpur",
    "रतलाम": "Ratlam",
    "उज्जैन": "Ujjain",
    "देवास": "Dewas",
    "मंदसौर": "Mandsaur",
    # Rajasthan
    "जयपुर": "Jaipur",
    "जोधपुर": "Jodhpur",
    "उदयपुर": "Udaipur",
    "कोटा": "Kota",
    "अजमेर": "Ajmer",
    "अलवर": "Alwar",
    "बीकानेर": "Bikaner",
    "श्रीगंगानगर": "Sriganganagar",
    # Uttar Pradesh
    "लखनऊ": "Lucknow",
    "कानपुर": "Kanpur",
    "वाराणसी": "Varanasi",
    "आगरा": "Agra",
    "मेरठ": "Meerut",
    "गोरखपुर": "Gorakhpur",
    "इलाहाबाद": "Allahabad",
    "प्रयागराज": "Prayagraj",
    # Delhi
    "दिल्ली": "Delhi",
    # Gujarat
    "सूरत": "Surat",
    "अहमदाबाद": "Ahmedabad",
    # Punjab / Haryana
    "अमृतसर": "Amritsar",
    "लुधियाना": "Ludhiana",
    "चंडीगढ़": "Chandigarh",
    "करनाल": "Karnal",
    "हिसार": "Hisar",
    "सोनीपत": "Sonipat",
    # Uttarakhand
    "हरिद्वार": "Haridwar Union APMC",
    "देहरादून": "Dehradun",
    # Other states
    "पटना": "Patna",
    "रांची": "Ranchi",
    "हैदराबाद": "Hyderabad",
    "बेंगलुरु": "Bangalore",
    "चेन्नई": "Chennai",
    "कोलकाता": "Kolkata",
    "रायपुर": "Raipur",
    "शिमला": "Shimla",
    "जम्मू": "Jammu",
}

# ── Hindi → English state map ─────────────────────────────────────────────────
STATE_MAP = {
    "मध्यप्रदेश": "Madhya Pradesh", "मध्य प्रदेश": "Madhya Pradesh",
    "उत्तरप्रदेश": "Uttar Pradesh", "उत्तर प्रदेश": "Uttar Pradesh",
    "राजस्थान": "Rajasthan", "महाराष्ट्र": "Maharashtra",
    "गुजरात": "Gujarat", "पंजाब": "Punjab", "हरियाणा": "Haryana",
    "बिहार": "Bihar", "पश्चिम बंगाल": "West Bengal",
    "कर्नाटक": "Karnataka", "तमिलनाडु": "Tamil Nadu",
    "तेलंगाना": "Telangana", "आंध्रप्रदेश": "Andhra Pradesh",
    "आंध्र प्रदेश": "Andhra Pradesh", "केरल": "Kerala",
    "ओडिशा": "Odisha", "छत्तीसगढ़": "Chhattisgarh",
    "झारखंड": "Jharkhand", "असम": "Assam",
    "हिमाचल प्रदेश": "Himachal Pradesh", "उत्तराखंड": "Uttarakhand",
    "उत्तराखण्ड": "Uttarakhand", "दिल्ली": "Delhi",
}


def _translate_commodity(commodity: str) -> str:
    en = COMMODITY_MAP.get(commodity.strip())
    if not en:
        for hindi, english in COMMODITY_MAP.items():
            if hindi in commodity:
                return english
        return commodity.strip().capitalize()
    return en


def _translate_market(market: str) -> str:
    m = market.strip()
    for suffix in ["मंडी", "मण्डी"]:
        m = m.replace(suffix, "").strip()
    return MARKET_MAP.get(m.strip(), m.strip().capitalize())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _fetch(params: dict) -> list:
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get("records", [])
    except requests.exceptions.RequestException as e:
        print(f"❌  API request failed: {e}")
        return []


def get_mandi_price(commodity: str, market: str, state: str) -> dict:
    commodity_en = _translate_commodity(commodity)
    market_en    = _translate_market(market) if market else ""

    print(f"🔄  Normalized → commodity: {commodity_en}, market: {market_en}")

    base_params = {
        "api-key":            DATA_GOV_API_KEY,
        "format":             "json",
        "filters[commodity]": commodity_en,
        "limit":              10,
    }

    # ── Fast path: direct market filter ─────────────────────────────────
    if market_en:
        records = _fetch({**base_params, "filters[market]": market_en})
        print(f"📄  Fast path ({market_en}): {len(records)} records")
        if records:
            return _build_result(records[0])
        print(f"⚠️  No exact match for '{market_en}', trying fuzzy …")

    # ── Fallback: fetch 100 records and fuzzy match ──────────────────────
    records = _fetch({**base_params, "limit": 100})
    print(f"📄  Fallback: fetched {len(records)} records")

    if not records:
        return {"error": "No mandi data found", "commodity": commodity_en}

    if market_en:
        best_score, best_record = 0.0, None
        for record in records:
            score = _similarity(market_en, record.get("market", ""))
            if score > best_score:
                best_score, best_record = score, record

        if best_record:
            print(f"🔍  Best fuzzy match: '{best_record.get('market')}' "
                  f"(score: {best_score:.2f})")
            if best_score >= 0.35:
                return _build_result(best_record)

        print("⚠️  No good market match — using first available record")

    return _build_result(records[0])


def _build_result(record: dict) -> dict:
    return {
        "commodity":   record.get("commodity"),
        "market":      record.get("market"),
        "state":       record.get("state"),
        "min_price":   record.get("min_price"),
        "max_price":   record.get("max_price"),
        "modal_price": record.get("modal_price"),
        "date":        record.get("arrival_date", "unknown"),
    }
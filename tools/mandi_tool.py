"""
tools/mandi_tool.py — Fetch mandi prices from Agmarknet government API

Commodity names verified directly from the actual dataset.
Sarvam Translate used as fallback for commodities not in the map.
"""

import requests
import os
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
SARVAM_API_KEY   = os.getenv("SARVAM_API_KEY")
BASE_URL         = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
TRANSLATE_URL    = "https://api.sarvam.ai/translate"

# ── Hindi → EXACT English commodity name as used in Agmarknet dataset ────────
# All names verified from actual dataset records
COMMODITY_MAP = {
    # Vegetables
    "टमाटर":       "Tomato",
    "आलू":         "Potato",
    "प्याज":       "Onion",
    "हरा प्याज":   "Onion Green",
    "लहसुन":       "Garlic",
    "अदरक":        "Ginger(Green)",
    "सूखा अदरक":   "Ginger(Dry)",
    "गोभी":        "Cauliflower",
    "फूलगोभी":     "Cauliflower",
    "पत्तागोभी":   "Cabbage",
    "बैंगन":       "Brinjal",
    "भिंडी":       "Bhindi(Ladies Finger)",
    "भिण्डी":      "Bhindi(Ladies Finger)",
    "करेला":       "Bitter gourd",
    "लौकी":        "Bottle gourd",
    "तोरई":        "Ridgeguard(Tori)",
    "मटर":         "Peas Wet",
    "हरी मटर":     "Green Peas",
    "मेथी":        "Methi(Leaves)",
    "पालक":        "Spinach",
    "धनिया":       "Coriander(Leaves)",
    "मिर्च":       "Green Chilli",
    "हरी मिर्च":   "Green Chilli",
    "लाल मिर्च":   "Dry Chillies",
    "मूली":        "Raddish",
    "गाजर":        "Carrot",
    "शिमला मिर्च": "Capsicum",
    "कद्दू":       "Pumpkin",
    "परवल":        "Pointed gourd(Parval)",
    "कटहल":        "Jack Fruit(Ripe)",
    "कुंदरू":      "Little gourd(Kundru)",
    "टिंडा":       "Tinda",
    "खीरा":        "Cucumbar(Kheera)",
    "चुकंदर":      "Beetroot",
    "शलजम":        "Turnip",
    "सहजन":        "Drumstick",
    "अरबी":        "Colacasia",
    "कच्चा केला":  "Banana - Green",
    "कच्चा आम":    "Mango(Raw-Ripe)",
    "शकरकंद":      "Sweet Potato",
    "जिमीकंद":     "Elephant Yam(Suran)/Amorphophallus",
    "रतालू":       "Yam(Ratalu)",
    "कचालू":       "Colacasia",
    "सर्पगुर्दा":  "Snakeguard",
    "तरोई":        "Ridgeguard(Tori)",
    "कद्दू":       "Ashgourd",
    "पेठा":        "Ashgourd",
    "टमाटर":       "Tomato",
    "चवली":        "Cowpea(Veg)",
    "ग्वार":       "Guar",
    "सेम":         "Beans",
    "फली":         "Beans",
    "चौलाई":       "Amaranthus",
    "पुदीना":      "Mint(Pudina)",
    "हल्दी":       "Turmeric",
    # Fruits
    "केला":        "Banana",
    "सेब":         "Apple",
    "आम":          "Mango",
    "अंगूर":       "Grapes",
    "संतरा":       "Orange",
    "मौसमी":       "Mousambi(Sweet Lime)",
    "मोसम्बी":     "Mousambi(Sweet Lime)",
    "पपीता":       "Papaya",
    "अनार":        "Pomegranate",
    "तरबूज":       "Water Melon",
    "खरबूजा":      "Karbuja(Musk Melon)",
    "नींबू":       "Lemon",
    "नीबू":        "Lime",
    "अमरूद":       "Guava",
    "नाशपाती":     "Pear",
    "अनानास":      "Pineapple",
    "चीकू":        "Chikoos(Sapota)",
    "सपोटा":       "Chikoos(Sapota)",
    "लीची":        "Litchi",
    "किन्नू":      "Kinnow",
    "कीवी":        "Kiwi Fruit",
    "नारियल":      "Coconut",
    "कच्चा नारियल":"Tender Coconut",
    "काली मिर्च":  "Black pepper",
    "इमली":        "Tamarind Fruit",
    "आंवला":       "Amla(Nelli Kai)",
    "स्ट्रॉबेरी":  "Strawberry",
    # Grains & Pulses
    "गेहूं":       "Wheat",
    "चावल":        "Rice",
    "धान":         "Paddy(Common)",
    "मक्का":       "Maize",
    "बाजरा":       "Bajra(Pearl Millet/Cumbu)",
    "ज्वार":       "Jowar(Sorghum)",
    "जौ":          "Barley(Jau)",
    "चना":         "Bengal Gram(Gram)(Whole)",
    "मसूर":        "Masur Dal",
    "मसूर दाल":    "Masur Dal",
    "मूंग":        "Green Gram(Moong)(Whole)",
    "मूंग दाल":    "Green Gram Dal(Moong Dal)",
    "उड़द":        "Black Gram(Urd Beans)(Whole)",
    "उड़द दाल":    "Black Gram Dal(Urd Dal)",
    "अरहर":        "Arhar(Tur/Red Gram)(Whole)",
    "तुवर दाल":    "Arhar Dal(Tur Dal)",
    "सोयाबीन":     "Soyabean",
    "सरसों":       "Mustard",
    "मूंगफली":     "Groundnut",
    "राई":         "Mustard",
    "ग्वार":       "Guar",
    # Cash crops & others
    "कपास":        "Cotton",
    "गन्ना":       "Sugarcane",
    "जीरा":        "Cummin Seed(Jeera)",
    "हल्दी":       "Turmeric",
    "सुपारी":      "Arecanut(Betelnut/Supari)",
    "काजू":        "Cashewnuts",
    "कॉफी":        "Coffee",
    "रबर":         "Rubber",
    "गुड़":        "Gur(Jaggery)",
    "मछली":        "Fish",
    "मशरूम":       "Mashrooms",
    "मकई":         "Maize",
}

# ── Hindi → EXACT English market name as in dataset ──────────────────────────
MARKET_MAP = {
    "अलीबाग": "Alibagh APMC", "मुरुड": "Murud APMC",
    "इंदौर": "Indore", "भोपाल": "Bhopal", "बड़वानी": "Badwani",
    "ग्वालियर": "Gwalior", "जबलपुर": "Jabalpur", "रतलाम": "Ratlam",
    "उज्जैन": "Ujjain", "देवास": "Dewas", "मंदसौर": "Mandsaur",
    "जयपुर": "Jaipur", "जोधपुर": "Jodhpur", "उदयपुर": "Udaipur",
    "कोटा": "Kota", "अजमेर": "Ajmer", "अलवर": "Alwar",
    "बीकानेर": "Bikaner", "श्रीगंगानगर": "Sriganganagar",
    "लखनऊ": "Lucknow", "कानपुर": "Kanpur", "वाराणसी": "Varanasi",
    "आगरा": "Agra", "मेरठ": "Meerut", "गोरखपुर": "Gorakhpur",
    "इलाहाबाद": "Allahabad", "प्रयागराज": "Prayagraj",
    "दिल्ली": "Delhi", "सूरत": "Surat", "अहमदाबाद": "Ahmedabad",
    "अमृतसर": "Amritsar", "लुधियाना": "Ludhiana", "चंडीगढ़": "Chandigarh",
    "करनाल": "Karnal", "हिसार": "Hisar", "सोनीपत": "Sonipat",
    "हरिद्वार": "Haridwar Union APMC", "देहरादून": "Dehradun",
    "पटना": "Patna", "रांची": "Ranchi", "हैदराबाद": "Hyderabad",
    "बेंगलुरु": "Bangalore", "चेन्नई": "Chennai", "कोलकाता": "Kolkata",
    "रायपुर": "Raipur", "शिमला": "Shimla", "जम्मू": "Jammu",
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


def _sarvam_translate(hindi_text: str) -> str:
    """Translate Hindi to English using Sarvam — fallback for unknown commodities."""
    try:
        resp = requests.post(
            TRANSLATE_URL,
            headers={"api-subscription-key": SARVAM_API_KEY},
            json={
                "input":                hindi_text,
                "source_language_code": "hi-IN",
                "target_language_code": "en-IN",
                "model":                "mayura:v1",
                "mode":                 "formal"
            },
            timeout=10
        )
        translated = resp.json().get("translated_text", "").strip()
        print(f"🌐  Sarvam Translate: '{hindi_text}' → '{translated}'")
        return translated or hindi_text.capitalize()
    except Exception as e:
        print(f"⚠️  Sarvam Translate failed: {e}")
        return hindi_text.capitalize()


def _translate_commodity(commodity: str) -> str:
    """
    Translate Hindi commodity to English.
    1. Sarvam Translate first (dynamic, no hardcoding)
    2. COMMODITY_MAP as fallback if translate fails or returns empty
    """
    # Step 1: Try Sarvam Translate
    translated = _sarvam_translate(commodity.strip())
    if translated and translated != commodity.strip().capitalize():
        return translated

    # Step 2: Fallback to COMMODITY_MAP
    print(f"⚠️  Sarvam Translate failed — falling back to COMMODITY_MAP")
    en = COMMODITY_MAP.get(commodity.strip())
    if en:
        return en
    for hindi, english in COMMODITY_MAP.items():
        if hindi in commodity:
            return english

    # Step 3: Last resort — return as-is
    return commodity.strip().capitalize()


def _translate_market(market: str) -> str:
    m = market.strip()
    # Strip common Hindi market suffixes
    for suffix in ["मंडी", "मण्डी", "एपीएमसी", "APMC"]:
        m = m.replace(suffix, "").strip()
    # Check map first
    mapped = MARKET_MAP.get(m.strip())
    if mapped:
        return mapped
    # Use Sarvam Translate for unknown markets
    translated = _sarvam_translate(m.strip())
    return translated if translated else m.strip().capitalize()


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

    print(f"  Normalized → commodity: {commodity_en}, market: {market_en}")

    base_params = {
        "api-key":            DATA_GOV_API_KEY,
        "format":             "json",
        "filters[commodity]": commodity_en,
        "limit":              10,
    }

    # ── Fast path: direct market filter ──────────────────────────────────
    if market_en:
        records = _fetch({**base_params, "filters[market]": market_en})
        print(f"  Fast path ({market_en}): {len(records)} records")
        if records:
            return _build_result(records[0])
        print(f"  No exact match for '{market_en}', trying fuzzy …")

    # ── Fallback: fetch 100 records and fuzzy match ───────────────────────
    records = _fetch({**base_params, "limit": 100})
    print(f"  Fallback: fetched {len(records)} records")

    if not records:
        return {"error": "No mandi data found", "commodity": commodity_en}

    if market_en:
        best_score, best_record = 0.0, None
        for record in records:
            score = _similarity(market_en, record.get("market", ""))
            if score > best_score:
                best_score, best_record = score, record

        if best_record and best_score >= 0.65:
            print(f"🔍  Fuzzy match: '{best_record.get('market')}' "
                  f"(score: {best_score:.2f})")
            return _build_result(best_record)

        print(f"❌  Market '{market_en}' not found in today's dataset")
        return {
            "error": "Market not found",
            "commodity": commodity_en,
            "market": market_en
        }

    # No market specified — return first available record
    if records:
        print(f"ℹ️  No market specified — returning first available record")
        return _build_result(records[0])

    return {"error": "No mandi data found", "commodity": commodity_en}


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
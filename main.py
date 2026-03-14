"""
main.py — FastAPI backend for Mandi Voice Assistant
"""

import io
import shutil
import time

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from services.asr_service import transcribe_audio
from services.llm_service import extract_entities
from services.tts_service import generate_speech_bytes
from tools.mandi_tool import get_mandi_price

app = FastAPI()


# ── Complete Hindi number lookup (0–99) ───────────────────────────────────────
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
    "01": "जनवरी",  "02": "फ़रवरी", "03": "मार्च",   "04": "अप्रैल",
    "05": "मई",     "06": "जून",    "07": "जुलाई",   "08": "अगस्त",
    "09": "सितंबर", "10": "अक्टूबर","11": "नवंबर",   "12": "दिसंबर",
}


def number_to_hindi(n: int) -> str:
    """Convert integer to Hindi words. Handles 0–9,999,999."""
    if n in HINDI_NUMBERS:
        return HINDI_NUMBERS[n]
    if n < 0:
        return "माइनस " + number_to_hindi(-n)
    if n < 1000:
        hun, rest = divmod(n, 100)
        return HINDI_NUMBERS[hun] + " सौ" + (" " + number_to_hindi(rest) if rest else "")
    if n < 100000:
        thou, rest = divmod(n, 1000)
        return number_to_hindi(thou) + " हज़ार" + (" " + number_to_hindi(rest) if rest else "")
    if n < 10000000:
        lakh, rest = divmod(n, 100000)
        return number_to_hindi(lakh) + " लाख" + (" " + number_to_hindi(rest) if rest else "")
    crore, rest = divmod(n, 10000000)
    return number_to_hindi(crore) + " करोड़" + (" " + number_to_hindi(rest) if rest else "")


def date_to_hindi(date_str: str) -> str:
    """Convert DD/MM/YYYY or YYYY-MM-DD to Hindi words."""
    try:
        if "/" in date_str:
            day, month, year = date_str.strip().split("/")
        elif "-" in date_str:
            year, month, day = date_str.strip().split("-")
        else:
            return date_str
        day_hindi   = number_to_hindi(int(day))
        month_hindi = HINDI_MONTHS.get(month.zfill(2), month)
        year_hindi  = number_to_hindi(int(year))
        return f"{day_hindi} {month_hindi} {year_hindi}"
    except Exception:
        return date_str


def generate_farmer_response(mandi_data: dict) -> str:
    """Convert mandi data to natural Hindi sentence with Hindi date and price."""
    if "error" in mandi_data:
        return "माफ कीजिए, इस मंडी का भाव अभी उपलब्ध नहीं है।"

    commodity = mandi_data["commodity"]
    market    = mandi_data["market"]
    price     = mandi_data["modal_price"]
    date      = mandi_data.get("date", "")

    try:
        price_hindi = number_to_hindi(int(float(price)))
    except Exception:
        price_hindi = str(price)

    date_text = ""
    if date and date != "unknown":
        date_text = f" {date_to_hindi(date)} को"

    return f"{market} मंडी में{date_text} {commodity} का भाव लगभग {price_hindi} रुपये प्रति क्विंटल है।"


@app.get("/")
def home():
    return {"message": "Mandi Voice Assistant Running"}


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):

    total_start = time.time()
    timings = {}

    print("\n" + "="*55)
    print("📥  New voice query received")
    print("="*55)

    # ── 1. Save temp audio ───────────────────────────────────────────────
    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # ── 2. ASR ───────────────────────────────────────────────────────────
    t = time.time()
    asr_result = transcribe_audio(file_path)
    timings["asr"] = round(time.time() - t, 2)
    transcript = asr_result.get("transcript", "")
    print(f"👂  ASR         : {transcript!r}")
    print(f"⏱️   ASR time    : {timings['asr']}s")

    if not transcript:
        response_text = "माफ कीजिए, आपकी आवाज़ समझ नहीं आई। कृपया दोबारा बोलें।"
        _print_summary(timings, total_start, success=False, reason="Empty transcript")
        return StreamingResponse(io.BytesIO(generate_speech_bytes(response_text)), media_type="audio/wav")

    # ── 3. Entity extraction ─────────────────────────────────────────────
    t = time.time()
    entities  = extract_entities(transcript)
    timings["llm"] = round(time.time() - t, 2)
    commodity = entities.get("commodity", "")
    market    = entities.get("market", "")
    state     = entities.get("state", "")
    print(f"📦  Entities    : commodity={commodity!r}  market={market!r}  state={state!r}")
    print(f"⏱️   LLM time    : {timings['llm']}s")

    if not commodity:
        response_text = "कृपया फसल का नाम बताएं जिसका भाव जानना है।"
        _print_summary(timings, total_start, success=False, reason="No commodity extracted")
        return StreamingResponse(io.BytesIO(generate_speech_bytes(response_text)), media_type="audio/wav")

    # ── 4. Mandi price ───────────────────────────────────────────────────
    t = time.time()
    mandi_data = get_mandi_price(commodity, market, state)
    timings["mandi_api"] = round(time.time() - t, 2)
    mandi_ok = "error" not in mandi_data
    print(f"📊  Mandi data  : {'✅ found' if mandi_ok else '❌ not found'}")
    print(f"📅  Price date  : {mandi_data.get('date', 'N/A')}")
    print(f"⏱️   Mandi time  : {timings['mandi_api']}s")

    # ── 5. Hindi response ────────────────────────────────────────────────
    response_text = generate_farmer_response(mandi_data)
    print(f"💬  Response    : {response_text}")

    # ── 6. TTS ───────────────────────────────────────────────────────────
    t = time.time()
    try:
        audio_bytes = generate_speech_bytes(response_text)
        timings["tts"] = round(time.time() - t, 2)
        print(f"⏱️   TTS time    : {timings['tts']}s")
    except Exception as e:
        timings["tts"] = round(time.time() - t, 2)
        print(f"⚠️  TTS Error   : {e}")
        audio_bytes = b""

    _print_summary(timings, total_start, success=mandi_ok)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")


def _print_summary(timings: dict, total_start: float, success: bool, reason: str = ""):
    total = round(time.time() - total_start, 2)
    print("\n" + "-"*55)
    print("📊  PERFORMANCE SUMMARY")
    print("-"*55)
    for step, t in timings.items():
        bar = "█" * int(t * 5)
        print(f"  {step:<12} {t:>6.2f}s  {bar}")
    print(f"  {'TOTAL':<12} {total:>6.2f}s")
    print(f"  Result      : {'✅ Success' if success else '❌ Failed' + (f' ({reason})' if reason else '')}")
    print("-"*55 + "\n")
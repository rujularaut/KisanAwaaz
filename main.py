"""
main.py — FastAPI backend for Mandi Voice Assistant
"""

import io
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from services.asr_service import transcribe_audio
from services.llm_service import extract_entities
from services.tts_service import generate_speech_bytes
from tools.mandi_tool import get_mandi_price

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Mandi Voice Assistant Running"}


def generate_farmer_response(mandi_data: dict) -> str:
    if "error" in mandi_data:
        return "माफ कीजिए, इस मंडी का भाव अभी उपलब्ध नहीं है।"
    commodity = mandi_data["commodity"]
    market    = mandi_data["market"]
    price     = mandi_data["modal_price"]
    return f"{market} मंडी में {commodity} का भाव लगभग {price} रुपये प्रति क्विंटल है।"


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    # ── 1. Save temp audio ───────────────────────────────────────────────
    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # ── 2. ASR ───────────────────────────────────────────────────────────
    asr_result = transcribe_audio(file_path)
    transcript = asr_result.get("transcript", "")
    print("👂  User said:", transcript)

    if not transcript:
        response_text = "माफ कीजिए, आपकी आवाज़ समझ नहीं आई। कृपया दोबारा बोलें।"
        return StreamingResponse(io.BytesIO(generate_speech_bytes(response_text)), media_type="audio/wav")

    # ── 3. Entity extraction ─────────────────────────────────────────────
    entities  = extract_entities(transcript)
    commodity = entities.get("commodity", "")
    market    = entities.get("market", "")
    state     = entities.get("state", "")
    print("📦  Entities:", entities)

    if not commodity:
        response_text = "कृपया फसल का नाम बताएं जिसका भाव जानना है।"
        return StreamingResponse(io.BytesIO(generate_speech_bytes(response_text)), media_type="audio/wav")

    # ── 4. Mandi price ───────────────────────────────────────────────────
    mandi_data = get_mandi_price(commodity, market, state)
    print("📊  Mandi Data:", mandi_data)

    # ── 5. Hindi response ────────────────────────────────────────────────
    response_text = generate_farmer_response(mandi_data)
    print("💬  Response:", response_text)

    # ── 6. TTS → stream WAV ──────────────────────────────────────────────
    try:
        audio_bytes = generate_speech_bytes(response_text)
    except Exception as e:
        print("⚠️  TTS Error:", e)
        audio_bytes = b""

    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
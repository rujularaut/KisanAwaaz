"""
main.py — FastAPI backend for KisanAwaaz with MCP pipeline

New flow:
1. ASR  — voice to Hindi text
2. MCP  — Sarvam-m decides tool → executes → generates Hindi response
3. TTS  — Hindi response to voice

The LLM now handles BOTH entity extraction AND response generation.
main.py just orchestrates ASR → MCP → TTS.
"""

import io
import shutil
import time

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from services.asr_service import transcribe_audio
from services.llm_service import process_farmer_query
from services.tts_service import generate_speech_bytes

app = FastAPI()


# ── Hindi number lookup (for logging only — LLM now generates response) ───────
HINDI_MONTHS = {
    "01": "जनवरी",  "02": "फ़रवरी", "03": "मार्च",   "04": "अप्रैल",
    "05": "मई",     "06": "जून",    "07": "जुलाई",   "08": "अगस्त",
    "09": "सितंबर", "10": "अक्टूबर","11": "नवंबर",   "12": "दिसंबर",
}


@app.get("/")
def home():
    return {"message": "KisanAwaaz — Mandi Voice Assistant with MCP"}


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    MCP-powered voice pipeline:
    1. ASR   → Hindi transcript
    2. MCP   → Sarvam-m calls tools → fetches price → generates Hindi response
    3. TTS   → Hindi audio → stream to client
    """

    total_start = time.time()
    timings     = {}

    print("\n" + "="*55)
    print("  New voice query received")
    print("="*55)

    # ── 1. Save temp audio ───────────────────────────────────────────────
    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # ── 2. ASR ───────────────────────────────────────────────────────────
    t          = time.time()
    asr_result = transcribe_audio(file_path)
    timings["asr"] = round(time.time() - t, 2)
    transcript = asr_result.get("transcript", "")
    print(f"  ASR         : {transcript!r}")
    print(f"  ASR time    : {timings['asr']}s")

    if not transcript:
        response_text = "माफ कीजिए, आपकी आवाज़ समझ नहीं आई। कृपया दोबारा बोलें।"
        _print_summary(timings, total_start, success=False, reason="Empty transcript")
        return StreamingResponse(
            io.BytesIO(generate_speech_bytes(response_text)),
            media_type="audio/wav"
        )

    # ── 3. MCP pipeline ──────────────────────────────────────────────────
    # Sarvam-m reads transcript → calls tool → gets price → generates response
    t      = time.time()
    result = process_farmer_query(transcript)
    timings["mcp"] = round(time.time() - t, 2)

    response_text = result["response_text"]
    mandi_data    = result.get("mandi_data", {})
    tool_called   = result.get("tool_called", "none")
    mandi_ok      = "error" not in mandi_data and bool(mandi_data)

    print(f"  Tool called : {tool_called}")
    print(f"  Mandi data  : {'✅ found' if mandi_ok else '❌ not found'}")
    print(f"  Price date  : {mandi_data.get('date', 'N/A')}")
    print(f"  Response    : {response_text}")
    print(f"   MCP time    : {timings['mcp']}s")

    # ── 4. TTS ───────────────────────────────────────────────────────────
    t = time.time()
    try:
        audio_bytes = generate_speech_bytes(response_text)
        timings["tts"] = round(time.time() - t, 2)
        print(f"   TTS time    : {timings['tts']}s")
    except Exception as e:
        timings["tts"] = round(time.time() - t, 2)
        print(f"  TTS Error   : {e}")
        audio_bytes = b""

    _print_summary(timings, total_start, success=mandi_ok)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")


def _print_summary(timings: dict, total_start: float, success: bool, reason: str = ""):
    total = round(time.time() - total_start, 2)
    print("\n" + "-"*55)
    print("  PERFORMANCE SUMMARY")
    print("-"*55)
    for step, t in timings.items():
        bar = "█" * int(t * 5)
        print(f"  {step:<12} {t:>6.2f}s  {bar}")
    print(f"  {'TOTAL':<12} {total:>6.2f}s")
    print(f"  Result      : {'✅ Success' if success else '❌ Failed' + (f' ({reason})' if reason else '')}")
    print("-"*55 + "\n")
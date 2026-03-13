"""
voice_client.py — Terminal voice client for Mandi Voice Assistant
Mic input  →  FastAPI  →  Speaker output (WAV via sounddevice)
No files created. Everything streams in memory.
"""

import io
import sys
import requests
import numpy as np
import sounddevice as sd
import soundfile as sf

API_URL    = "http://127.0.0.1:8000/voice-query"
SAMPLERATE = 16000
CHUNK_MS   = 100
THRESHOLD  = 300
SILENCE_S  = 2.0
MAX_S      = 15


# ── Recording ────────────────────────────────────────────────────────────────

def record_from_mic() -> io.BytesIO:
    chunk              = int(SAMPLERATE * CHUNK_MS / 1000)
    max_chunks         = int(MAX_S * 1000 / CHUNK_MS)
    need_silent_chunks = int(SILENCE_S * 1000 / CHUNK_MS)

    frames: list[np.ndarray] = []
    silent_chunks  = 0
    speech_started = False

    print("\n🎤  Listening … speak your query")

    with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="int16") as stream:
        for _ in range(max_chunks):
            data, _ = stream.read(chunk)
            rms = int(np.sqrt(np.mean(data.astype(np.float32) ** 2)))

            if rms > THRESHOLD:
                speech_started = True
                silent_chunks  = 0
            elif speech_started:
                silent_chunks += 1

            if speech_started:
                frames.append(data.copy())

            if speech_started and silent_chunks >= need_silent_chunks:
                print("🔇  Done speaking — processing …")
                break
        else:
            if not speech_started:
                print("⚠️  No speech detected. Lower THRESHOLD if needed.")
                sys.exit(1)
            print("⏱️  Max time reached — processing …")

    audio = np.concatenate(frames, axis=0)
    print(f"✅  Recorded {len(audio)/SAMPLERATE:.1f}s")

    buf = io.BytesIO()
    sf.write(buf, audio, SAMPLERATE, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return buf


# ── API call ─────────────────────────────────────────────────────────────────

def query_api(wav_buf: io.BytesIO) -> bytes:
    print("📡  Sending to server …")
    try:
        resp = requests.post(
            API_URL,
            files={"audio": ("query.wav", wav_buf, "audio/wav")},
            timeout=120
        )
    except requests.exceptions.ConnectionError:
        print("❌  Cannot reach server. Run:  uvicorn main:app --reload")
        sys.exit(1)
    except requests.exceptions.ReadTimeout:
        print("❌  Server took too long. Try again.")
        return b""

    if resp.status_code != 200:
        print(f"❌  Server error {resp.status_code}: {resp.text}")
        return b""

    return resp.content


# ── Playback — WAV bytes via sounddevice (no files, pure terminal) ────────────

def play_audio(wav_bytes: bytes) -> None:
    if not wav_bytes or len(wav_bytes) < 100:
        print("⚠️  No audio received — check server logs.")
        return

    print("🔊  Playing response …")
    try:
        buf = io.BytesIO(wav_bytes)
        data, samplerate = sf.read(buf, dtype="int16")
        sd.play(data, samplerate)
        sd.wait()
        print("✅  Done.\n")
    except Exception as e:
        print(f"⚠️  Playback error: {e}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("   🌾  Mandi Voice Assistant")
    print("   Speak in Hindi — hear prices instantly")
    print("=" * 52)

    while True:
        try:
            input("\n▶  Press Enter to speak  (Ctrl+C to quit) … ")
        except KeyboardInterrupt:
            print("\n👋  Goodbye!")
            break

        wav = record_from_mic()
        audio_bytes = query_api(wav)
        play_audio(audio_bytes)


if __name__ == "__main__":
    main()
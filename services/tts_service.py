import requests
import base64
import os
from dotenv import load_dotenv
load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TTS_URL = "https://api.sarvam.ai/text-to-speech"


def generate_speech_bytes(text: str) -> bytes:
    """
    Call Sarvam TTS API and return raw WAV bytes.
    Sarvam returns JSON with base64-encoded audio in response["audios"][0].
    """
    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }
    payload = {
        "text": text,
        "model": "bulbul:v3",
        "voice": "female",
        "language": "hi-IN"
    }

    response = requests.post(TTS_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"TTS API Error: {response.text}")

    data = response.json()

    # Sarvam returns: {"audios": ["<base64 encoded WAV>", ...]}
    audios = data.get("audios", [])
    if not audios:
        raise Exception(f"TTS returned no audio. Response: {data}")

    # Decode base64 → raw WAV bytes
    wav_bytes = base64.b64decode(audios[0])
    print(f"✅  TTS decoded {len(wav_bytes)} bytes of WAV audio")

    return wav_bytes
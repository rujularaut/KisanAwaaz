import requests
import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

ASR_URL = "https://api.sarvam.ai/speech-to-text"


def transcribe_audio(audio_file_path):

    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

    files = {
        "file": (audio_file_path, open(audio_file_path, "rb"), "audio/wav")
    }

    data = {
    "model": "saaras:v3"
}

    response = requests.post(
        ASR_URL,
        headers=headers,
        files=files,
        data=data
    )

    return response.json()
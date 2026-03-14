<<<<<<< HEAD
# 🌾 KisanAwaaz — Mandi Voice Assistant

A voice-based assistant for Indian farmers that provides **real-time mandi (wholesale market) prices** of agricultural commodities in **Hindi**.

Farmers speak a query in Hindi → the system understands it → fetches live prices → responds back in Hindi voice.

---

## 🎯 Features

- 🎤 **Voice Input** — speak naturally in Hindi from your terminal microphone
- 🧠 **AI Entity Extraction** — extracts commodity, market, and state from spoken queries
- 📊 **Live Mandi Prices** — fetches real-time data from the Government of India's Agmarknet dataset
- 🔊 **Hindi Voice Output** — responds with prices spoken aloud in Hindi
- 📅 **Date Aware** — tells you when the price was last recorded
- ⚡ **Fast** — full pipeline completes in 4–8 seconds

---

## 🏗️ Architecture

```
[Farmer speaks Hindi]
        ↓
[Microphone] → voice_client.py
        ↓
[FastAPI /voice-query endpoint] → main.py
        ↓
[ASR] → Sarvam AI (saaras:v3) → Hindi transcript
        ↓
[LLM] → Sarvam AI (sarvam-m) → commodity, market, state
        ↓
[Mandi API] → data.gov.in Agmarknet → live price data
        ↓
[TTS] → Sarvam AI (bulbul:v3) → Hindi audio
        ↓
[Speaker] → plays response on terminal
```

---

## 📁 Project Structure

```
backend/
├── main.py                  # FastAPI app — full voice pipeline
├── voice_client.py          # Terminal mic input + speaker output
├── requirements.txt         # Python dependencies
├── .env                     # API keys (never commit this)
├── .gitignore
├── services/
│   ├── asr_service.py       # Speech to text (Sarvam saaras:v3)
│   ├── llm_service.py       # Entity extraction (Sarvam sarvam-m)
│   └── tts_service.py       # Text to speech (Sarvam bulbul:v3)
└── tools/
    └── mandi_tool.py        # Agmarknet price fetch + fuzzy matching
```

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/rujularaut/KisanAwaaz.git
cd KisanAwaaz/backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file
Create a file named `.env` in the `backend/` folder:
```
SARVAM_API_KEY=your_sarvam_api_key_here
DATA_GOV_API_KEY=your_data_gov_api_key_here
```

Get your API keys:
- **Sarvam API** → https://console.sarvam.ai (free tier available)
- **Data.gov.in API** → https://data.gov.in (free registration)

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Run the voice client (in a new terminal)
```bash
python voice_client.py
```

---

## 🎤 How to Use

1. Start the server in Terminal 1
2. Start the voice client in Terminal 2
3. Press **Enter** to begin speaking
4. Ask your query in Hindi, for example:
   - *"बड़वानी मंडी में टमाटर का भाव क्या है?"*
   - *"जयपुर मंडी में प्याज का दाम बताओ"*
   - *"हरिद्वार मंडी में आलू का भाव क्या है?"*
5. Wait 4–8 seconds — the assistant will speak the price back in Hindi
6. Press **Enter** again for another query, or **Ctrl+C** to quit

---

## 🗣️ Sample Queries

| Query | Meaning |
|-------|---------|
| बड़वानी मंडी में टमाटर का भाव क्या है? | Tomato price at Badwani mandi |
| जयपुर मंडी में प्याज का दाम बताओ | Onion price at Jaipur mandi |
| हरिद्वार मंडी में आलू का भाव क्या है? | Potato price at Haridwar mandi |
| इंदौर मंडी में गेहूं का भाव बताओ | Wheat price at Indore mandi |
| नासिक मंडी में अंगूर का भाव क्या है? | Grape price at Nashik mandi |
| राजस्थान में गाजर का भाव बताओ | Carrot price in Rajasthan |

---

## 📊 Performance

Typical response times:

| Step | Time |
|------|------|
| ASR (speech to text) | 0.5 – 2s |
| LLM (entity extraction) | 0.4 – 1s |
| Mandi API (price fetch) | 1 – 3s |
| TTS (text to speech) | 2 – 4s |
| **Total** | **4 – 8s** |

---

## 🔧 Configuration

Adjust these variables at the top of `voice_client.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `THRESHOLD` | `300` | Mic sensitivity — lower if mic doesn't pick up voice |
| `SILENCE_S` | `2.0` | Seconds of silence before auto-stop |
| `MAX_S` | `15` | Maximum recording duration in seconds |

---

## ⚠️ Known Limitations

- The Agmarknet dataset only includes markets that have reported prices for that day — some markets may return no data on certain days
- `sarvam-m` LLM occasionally takes longer on peak hours
- Maharashtra dataset has limited market coverage in Agmarknet

---

## 🛠️ Troubleshooting

**Mic not detected / no speech captured**
```
Lower THRESHOLD in voice_client.py from 300 to 150
```

**Server not starting**
```
Make sure .env file exists with valid API keys
Run: pip install -r requirements.txt
```

**"भाव उपलब्ध नहीं है" (price not available)**
```
That market/commodity combination has no data today.
Try a different market or commodity.
Use check_markets.py to see what's available.
```

**LLM timeout**
```
Sarvam servers may be overloaded. Wait and retry.
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Backend API server |
| `uvicorn` | ASGI server to run FastAPI |
| `requests` | HTTP calls to Sarvam and Agmarknet APIs |
| `sounddevice` | Mic recording and speaker playback |
| `soundfile` | WAV audio encoding/decoding |
| `numpy` | Audio buffer processing |
| `python-dotenv` | Load API keys from .env file |

---

## 👨‍💻 Built With

- [Sarvam AI](https://sarvam.ai) — ASR, LLM, TTS in Hindi
- [Agmarknet / data.gov.in](https://data.gov.in) — Live mandi price data
- [FastAPI](https://fastapi.tiangolo.com) — Backend framework

---

## 📄 License

MIT License — free to use and modify.
=======
\# Mandi Voice Assistant 🌾



Voice-based assistant for Indian farmers to get real-time mandi prices in Hindi.



\## Setup

1\. Clone the repo

2\. Create a `.env` file with:

SARVAM\_API\_KEY=your\_key\_here

DATA\_GOV\_API\_KEY=your\_key\_here

3\. Install dependencies:

pip install fastapi uvicorn sounddevice soundfile pygame numpy requests python-dotenv anthropic

4\. Run the server: uvicorn main:app --reload

5\. Run the client: python voice\_client.py

>>>>>>> ca18bf9 (Add KisanAwaaz prototype updates and fixes)

# KisanAwaaz – Hindi Voice-Based AI Mandi Price Assistant

KisanAwaaz, meaning **"Farmer's Voice"**, is a voice-first AI assistant that helps Indian farmers access real-time mandi prices in Hindi.

Farmers can speak a query in Hindi, such as:

> "बड़वानी मंडी में टमाटर का भाव क्या है?"

The system understands the spoken query, fetches live mandi price data, generates a Hindi response, and speaks it back to the farmer.

The goal of KisanAwaaz is to make government-published agricultural market data accessible to farmers who may not be comfortable with reading, typing, using apps, or navigating online portals.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Demo Workflow](#demo-workflow)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Example Queries](#example-queries)
- [API and Data Source](#api-and-data-source)
- [MCP-Style Tool Calling](#mcp-style-tool-calling)
- [Fallback Mechanism](#fallback-mechanism)
- [Performance](#performance)
- [Cost Estimation](#cost-estimation)
- [Use Cases](#use-cases)
- [Future Scope](#future-scope)
- [Built At](#built-at)
- [Author](#author)

---

## Problem Statement

The Government of India publishes daily mandi prices for agricultural commodities through the Agmarknet platform on data.gov.in.

This data is useful because it helps farmers understand the current wholesale market price of crops across different mandis.

However, many smallholder farmers face barriers such as:

- Difficulty reading or typing
- Limited digital literacy
- Difficulty navigating websites or apps
- Language barriers
- Dependence on middlemen for price information
- Lack of simple voice-based access to mandi price data

Because of this, many farmers may not get transparent market price information before selling their produce.

---

## Solution

KisanAwaaz removes the need for reading, typing, or app navigation.

The farmer only needs to:

1. Press a button
2. Speak a question in Hindi
3. Listen to the mandi price response in Hindi

The system works as an end-to-end voice AI pipeline:

Farmer's Voice Query
        ↓
Speech-to-Text
        ↓
Query Understanding
        ↓
MCP-Style Tool Selection
        ↓
Agmarknet API / CSV Fallback
        ↓
Hindi Response Generation
        ↓
Text-to-Speech
        ↓
Spoken Answer

## Key Features
Hindi voice-based interaction
No reading or typing required
Real-time mandi price fetching
Uses Government of India's Agmarknet data
Supports commodity and mandi-based queries
MCP-style intelligent tool calling
CSV fallback when live API is unavailable
Hindi speech recognition
Hindi text-to-speech response
Low-cost query processing
FastAPI-based backend
Designed for accessibility and rural use cases

## Demo Workflow

Example farmer query:

```
बड़वानी मंडी में टमाटर का भाव क्या है?
```

System flow:

Farmer speaks the query in Hindi.
Audio is converted to text using ASR.
The system understands the commodity and mandi name.
The MCP-style tool-calling layer selects the correct tool.
The tool fetches mandi price data from Agmarknet API.
A Hindi response is generated.
The response is converted to speech.
The farmer hears the answer.

Example response:
```
बड़वानी मंडी में टमाटर का न्यूनतम भाव 1200 रुपये, अधिकतम भाव 1800 रुपये और मॉडल भाव 1500 रुपये प्रति क्विंटल है।
```

## System Architecture
```
+----------------------+
| Farmer Voice Input   |
+----------+-----------+
           |
           v
+----------------------+
| Audio Recording      |
| Voice Activity Logic |
+----------+-----------+
           |
           v
+----------------------+
| Sarvam AI ASR        |
| Speech to Text       |
+----------+-----------+
           |
           v
+----------------------+
| Query Understanding  |
| Intent Detection     |
+----------+-----------+
           |
           v
+----------------------+
| MCP-Style Tool Layer |
| get_mandi_price      |
| get_best_mandi       |
+----------+-----------+
           |
           v
+----------------------+
| Agmarknet API        |
| CSV Backup           |
+----------+-----------+
           |
           v
+----------------------+
| Hindi Response       |
| Generation           |
+----------+-----------+
           |
           v
+----------------------+
| Sarvam AI TTS        |
| Text to Speech       |
+----------+-----------+
           |
           v
+----------------------+
| Spoken Hindi Output  |
+----------------------+
```

## Tech Stack
Area	Technology
Backend	Python, FastAPI
AI Models	Sarvam AI
Speech-to-Text	Sarvam Saaras v3
LLM / Response Generation	Sarvam-m
Text-to-Speech	Sarvam Bulbul v3
Translation	Sarvam Translate
Tool Calling	MCP-style tool layer
Data Source	Agmarknet API, data.gov.in
Data Processing	Pandas
Fallback Storage	CSV
Audio Handling	sounddevice, soundfile
Environment Management	python-dotenv


## How It Works
### 1. Voice Input

The farmer speaks a query in Hindi.

Example:
```
इंदौर मंडी में प्याज का भाव क्या है?
```
The system records the audio through a microphone.

### 2. Speech-to-Text

The recorded Hindi audio is passed to Sarvam AI's ASR model.

The ASR model converts speech into Hindi text.

Example:
```
इंदौर मंडी में प्याज का भाव क्या है?
```

### 3. Query Understanding

The system identifies important information from the query:

- Commodity name
- Mandi name
- Type of request

Example:
```
Commodity: प्याज
Mandi: इंदौर
Intent: Get mandi price
```

### 4. Translation

If required, Hindi commodity and mandi names are translated or normalized for API compatibility.

Example:
```
प्याज → Onion
इंदौर → Indore
```

### 5. MCP-Style Tool Calling

The system selects the correct tool based on the user's query.

Available tools:
```
get_mandi_price
get_best_mandi
```
If the farmer asks for the price in a specific mandi, the system uses:
```
get_mandi_price
```
If the farmer asks where they can get the best price, the system uses:
```
get_best_mandi
```

### 6. Data Fetching

The selected tool queries the Agmarknet API from data.gov.in.

The system fetches:

Market name
Commodity
Minimum price
Maximum price
Modal price
Arrival date

### 7. CSV Fallback

If the live API is unavailable or fails, the system uses a local CSV backup.

This improves reliability and prevents the system from completely failing during API downtime.

### 8. Hindi Response Generation

The system creates a natural Hindi response.

Example:
```
इंदौर मंडी में प्याज का मॉडल भाव 1800 रुपये प्रति क्विंटल है।
```

### 9. Text-to-Speech

The Hindi response is converted into speech using Sarvam AI TTS.

### 10. Spoken Output

The farmer hears the answer in Hindi.

## Project Structure

You can update this section based on your actual folder names.
```
KisanAwaaz/
│
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment and API configuration
│   ├── audio.py                 # Audio recording and playback logic
│   ├── asr.py                   # Speech-to-text integration
│   ├── tts.py                   # Text-to-speech integration
│   ├── translator.py            # Hindi-English translation logic
│   ├── tools.py                 # MCP-style tool functions
│   ├── agmarknet.py             # Agmarknet API integration
│   ├── fallback.py              # CSV fallback logic
│   └── response_generator.py    # Hindi response generation
│
├── data/
│   └── mandi_prices_backup.csv  # Local CSV fallback data
│
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

## Installation and Setup
### 1. Clone the Repository
```
git clone https://github.com/rujularaut/KisanAwaaz.git
cd KisanAwaaz
```
### 2. Create a Virtual Environment
```
python -m venv venv
```
Activate it:

For Windows:
```
venv\Scripts\activate
```
For macOS/Linux:
```
source venv/bin/activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
## Environment Variables

Create a .env file in the root directory.
```
SARVAM_API_KEY=your_sarvam_api_key
DATA_GOV_API_KEY=your_data_gov_api_key
AGMARKNET_API_URL=your_agmarknet_api_url
```
You can also create a .env.example file:
```
SARVAM_API_KEY=
DATA_GOV_API_KEY=
AGMARKNET_API_URL=
```

## Running the Project
Start the FastAPI server:
```
uvicorn app.main:app --reload
```
The server will run at:
```
http://127.0.0.1:8000
```
Interactive API docs:
```
http://127.0.0.1:8000/docs
```
If your project has a terminal-based voice client, run:
```
python voice_client.py
```

## Example Queries

Farmers can ask questions like:
```
बड़वानी मंडी में टमाटर का भाव क्या है?
```
```
इंदौर मंडी में प्याज का रेट बताओ
```
```
आज गेहूं का सबसे अच्छा भाव कहां मिल रहा है?
```
```
नासिक मंडी में आलू का भाव क्या है?
```
```
सोयाबीन का सबसे ज्यादा भाव किस मंडी में है?
```

## API and Data Source

KisanAwaaz uses the Government of India's Agmarknet data available through data.gov.in.

The API provides mandi price information such as:

State
District
Market
Commodity
Variety
Arrival date
Minimum price
Maximum price
Modal price

The system queries this data based on the farmer's spoken input.

## MCP-Style Tool Calling

KisanAwaaz uses an MCP-style tool calling layer.

This means the AI system does not directly answer everything by itself. Instead, it decides which tool should be used to get accurate real-time data.

### Tool 1: get_mandi_price

Used when the user asks for the price of a commodity in a specific mandi.

Example:
```
बड़वानी मंडी में टमाटर का भाव क्या है?
```
Expected tool:
```
get_mandi_price(commodity="Tomato", market="Badwani")
```
### Tool 2: get_best_mandi

Used when the user asks where the best price is available.

Example:
```
गेहूं का सबसे अच्छा भाव कहां मिल रहा है?
```
Expected tool:
```
get_best_mandi(commodity="Wheat")
```

## Fallback Mechanism

Sometimes the live API may fail due to:

Network issues
API downtime
Rate limits
Invalid response
Missing records

To handle this, KisanAwaaz uses a local CSV fallback.
```
Live API available → Fetch latest data from Agmarknet
Live API unavailable → Use local CSV backup
```
This makes the system more reliable for real-world usage.

## Performance

The system is designed to return a spoken Hindi response in under 11 seconds.

The total time includes:

Audio recording
Speech-to-text conversion
Query understanding
API fetching
Response generation
Text-to-speech conversion
Audio playback

## Cost Estimation

The estimated cost per query is approximately:
```
8.5 paise per query
```
This makes the solution cost-effective and scalable for large-scale rural deployment.

## Use Cases

KisanAwaaz can be useful for:

Smallholder farmers
Farmer Producer Organizations
Agricultural helpline systems
Rural kiosks
WhatsApp voice bot extensions
Government agriculture support services
NGOs working in rural digital inclusion
Mandi price awareness campaigns

## Future Scope

Possible improvements include:

WhatsApp voice integration
IVR phone-call based access
Support for more Indian languages
Offline-first mobile app
Farmer location-based mandi suggestions
Price trend prediction
Crop recommendation based on market rates
Multilingual speech support
SMS backup for low-network regions
Dashboard for mandi price analytics
Integration with weather and crop advisory APIs

## Built At

KisanAwaaz was built at SheInspires 2.0, an all-women AI Hackathon organized by Zensar, RPG Foundation, and MIT ADT University in March 2026.

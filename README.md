 # Mandi Voice Assistant 



Voice-based assistant for Indian farmers to get real-time mandi prices in Hindi.



## Setup

1\. Clone the repo

2\. Create a `.env` file with:

SARVAM\_API\_KEY=your\_key\_here

DATA\_GOV\_API\_KEY=your\_key\_here

3\. Install dependencies:

pip install fastapi uvicorn sounddevice soundfile pygame numpy requests python-dotenv anthropic

4\. Run the server: uvicorn main:app --reload

5\. Run the client: python voice\_client.py


"""
check_markets.py — Find all markets available in a specific state
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

def check_markets_for_state(state_name: str):
    params = {
        "api-key":          DATA_GOV_API_KEY,
        "format":           "json",
        "filters[state]":   state_name,
        "limit":            100,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        records = resp.json().get("records", [])
        if not records:
            print(f"❌  No data found for state: {state_name}")
            return

        # Get unique markets
        markets = {}
        for r in records:
            market = r.get("market")
            commodity = r.get("commodity")
            if market not in markets:
                markets[market] = []
            markets[market].append(commodity)

        print(f"\n✅  Markets available in '{state_name}' ({len(markets)} found):")
        print("-"*50)
        for market, commodities in sorted(markets.items()):
            print(f"  {market:<40} {', '.join(commodities[:3])}")

    except Exception as e:
        print(f"⚠️  Error: {e}")

check_markets_for_state("Maharashtra")
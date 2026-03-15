"""
check_markets.py — Find all markets available for a specific commodity today
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

def find_markets_for_commodity(commodity: str):
    all_records = []
    offset = 0

    while True:
        params = {
            "api-key":            DATA_GOV_API_KEY,
            "format":             "json",
            "filters[commodity]": commodity,
            "limit":              100,
            "offset":             offset,
        }
        try:
            resp    = requests.get(BASE_URL, params=params, timeout=15)
            records = resp.json().get("records", [])
        except Exception as e:
            print(f"❌ Error: {e}")
            break

        if not records:
            break
        all_records.extend(records)
        if len(records) < 100:
            break
        offset += 100

    print(f"\n✅  Markets available for '{commodity}' today ({len(all_records)} records):")
    print("-"*65)
    print(f"  {'Market':<40} {'State':<20} {'Price'}")
    print("-"*65)
    for r in sorted(all_records, key=lambda x: x.get("state","")):
        print(f"  {r.get('market',''):<40} {r.get('state',''):<20} ₹{r.get('modal_price','')}")

    print(f"\n💬  Sample Hindi queries you can ask:")
    print("-"*65)
    for r in all_records[:10]:
        market = r.get("market", "").replace(" APMC","").replace("(F&V)","").strip()
        print(f"  {market} मंडी में {commodity} का भाव क्या है?")

find_markets_for_commodity("Potato")
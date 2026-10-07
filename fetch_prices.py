import requests
import time
import pandas as pd
import io
import sys


API_URL = "https://openstat.psa.gov.ph:443/PXWeb/api/v1/en/DB/2M/NFG/0032M4AFN02.px"

query_payload = {
    "query": [
        {"code": "Geolocation", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Commodity", "selection": {"filter": "item", "values": ["0"]}}, 
        {"code": "Year", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Period", "selection": {"filter": "all", "values": ["*"]}},
    ],
    "response": {"format": "csv"}
}

def fetch_with_retries(url, payload, attempts=3, timeout=60):
    """POST to the PXWeb endpoint, retrying on network errors and non-200 responses."""
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            print(f"📡 Contacting OpenSTAT server (attempt {attempt}/{attempts})...")
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp
            print(f"❌ Target server refused transmission. Status: {resp.status_code}")
            print(resp.text[:500])
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            print(f"🔌 Request error on attempt {attempt}: {e}")
            last_err = str(e)
        if attempt < attempts:
            wait = 5 * attempt
            print(f"   retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"giving up after {attempts} attempts ({last_err})")

def main():
    response = fetch_with_retries(API_URL, query_payload)

    df_wide = pd.read_csv(io.StringIO(response.text), na_values=[".", "..", ":", "-"])
    print(df_wide)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"🔌 Critical pipeline error: {e}")
        sys.exit(1)  
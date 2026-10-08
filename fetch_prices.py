from pathlib import Path
import requests
import time
import pandas as pd
import io
import sys
import json
from datetime import datetime


API_URL = "https://openstat.psa.gov.ph:443/PXWeb/api/v1/en/DB/2M/NFG/0032M4AFN02.px"

query_payload = {
    "query": [
        {"code": "Geolocation", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Commodity", "selection": {"filter": "all", "values": ["*"]}}, 
        {"code": "Year", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Period", "selection": {"filter": "all", "values": ["*"]}},
    ],
    "response": {"format": "csv"}
}

OUT_DIR = Path(__file__).parent / "web" / "agricultural-prices" / "public" / "data"
CSV_PATH = OUT_DIR / "agricultural-prices.csv"
JSON_PATH = OUT_DIR / "agricultural-prices.json"
META_PATH = OUT_DIR / "agricultural-prices-meta.json"

def fetch_with_retries(url, payload, attempts=3, timeout=60):
    """POST to the PXWeb endpoint, retrying on network errors and non-200 responses."""
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            print(f" Contacting OpenSTAT server (attempt {attempt}/{attempts})...")
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp
            print(f" Target server refused transmission. Status: {resp.status_code}")
            print(resp.text[:500])
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            print(f" Request error on attempt {attempt}: {e}")
            last_err = str(e)
        if attempt < attempts:
            wait = 5 * attempt
            print(f"   retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"giving up after {attempts} attempts ({last_err})")

def main():
    response = fetch_with_retries(API_URL, query_payload)

    df_wide = pd.read_csv(io.StringIO(response.text), na_values=[".", "..", ":", "-"])

    id_cols = ["Geolocation", "Commodity"]
    value_cols = [c for c in df_wide.columns if c not in id_cols]
    df = df_wide.melt(id_vars=id_cols, value_vars=value_cols, var_name="YearPeriod", value_name="Price_PHP")

    split_cols = df["YearPeriod"].str.extract(r"^(\d{4})\s+(.+)$")
    df["Year"] = split_cols[0].astype(int)
    df["Month"] = split_cols[1]
    df = df[df["Month"] != "Annual"].copy()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    df.to_json(JSON_PATH, orient="records", indent=2, force_ascii=False)
    META_PATH.write_text(json.dumps({
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "rows": len(df),
    }, indent=2))

    print(df.head())


    print(f"wrote {len(df_wide)} rows to {CSV_PATH}, {JSON_PATH}, and {META_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f" Critical pipeline error: {e}")
        sys.exit(1)  
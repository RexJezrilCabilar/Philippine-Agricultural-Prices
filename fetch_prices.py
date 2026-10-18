from pathlib import Path
import requests
import time
import pandas as pd
import io
import sys
import json
from datetime import datetime
from scipy.stats import linregress


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
CSV_PATH2 = OUT_DIR / "forecast-data.csv"
META_PATH = OUT_DIR / "agricultural-prices-meta.json"

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

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


def get_regression_metrics(group):
    if len(group) < 2:
        return pd.Series({"slope": None, "intercept": None})

    res = linregress(group["Month_Num"], group["Price_PHP"])


    return pd.Series({
        "slope": res.slope, 
        "intercept": res.intercept
        })

def main():
    response = fetch_with_retries(API_URL, query_payload)

    df_wide = pd.read_csv(io.StringIO(response.text), na_values=[".", "..", ":", "-"])
    

    #Cleaning the dataset
    id_cols = ["Geolocation", "Commodity"]
    value_cols = [c for c in df_wide.columns if c not in id_cols]
    df = df_wide.melt(id_vars=id_cols, value_vars=value_cols, var_name="YearPeriod", value_name="Price_PHP")

    split_cols = df["YearPeriod"].str.extract(r"^(\d{4})\s+(.+)$")
    df["Year"] = split_cols[0].astype(int)
    df["Month"] = split_cols[1]
    df = df[df["Month"] != "Annual"].copy()

    df["Price_PHP"] = pd.to_numeric(df["Price_PHP"], errors="coerce")
    df = df.dropna(subset="Price_PHP")
    df = df[df["Price_PHP"] != 0]

    if df.empty:
        raise RuntimeError("parsed 0 rows - PSA might have changed their table structure")

    df["Month_Num"] = df["Month"].map(MONTH_MAP)
    latest_price = df.groupby(["Geolocation", "Commodity"]).last().reset_index()
    latest_price["Geolocation"] = latest_price["Geolocation"].str.replace("......", "", regex=False)
    latest_price["Geolocation"] = latest_price["Geolocation"].str.replace("....", "", regex=False)
    latest_price["Geolocation"] = latest_price["Geolocation"].str.replace("..", "", regex=False)


    #Getting the data needed for the forecast
    df = df[df["Year"] == 2026]
    df["Geolocation"] = df["Geolocation"].str.replace("......", "", regex=False)
    df["Geolocation"] = df["Geolocation"].str.replace("....", "", regex=False)
    df["Geolocation"] = df["Geolocation"].str.replace("..", "", regex=False)

    regression_results = df.groupby(["Geolocation", "Commodity"]).apply(get_regression_metrics, include_groups=False)
    regression_results = regression_results.reset_index()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest_price.to_csv(CSV_PATH, index=False)
    latest_price.to_json(JSON_PATH, orient="records", indent=2, force_ascii=False)
    regression_results.to_csv(CSV_PATH2, index=False)
    META_PATH.write_text(json.dumps({
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "rows": len(df),
    }, indent=2))

    print(df.head(20))



    print(f"wrote {len(df_wide)} rows to {CSV_PATH}, {JSON_PATH}, and {META_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f" Critical pipeline error: {e}")
        sys.exit(1)  
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from openai import OpenAI

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])


client = OpenAI(
    api_key = os.environ["LLM_API_KEY"],
    base_url = os.environ["LLM_BASE_URL"]  
)
MODEL = os.environ["LLM_MODEL"]

query = """
SELECT c.commodity, g.geolocation, p.price_this_month, p.price_next_month, p.price_in_two_months
FROM prices p
JOIN commodity c ON c.commodity_id = p.commodity_id
JOIN geolocation g ON g.geolocation_id = p.geolocation_id 
"""

df = pd.read_sql(query, engine)
df = df.dropna()
print(df.shape)


cols = ["price_this_month", "price_next_month", "price_in_two_months"]
summary = df.groupby("commodity")[cols].mean().round(2).reset_index()
summary["change_pct"] = (
    (summary["price_in_two_months"] - summary["price_this_month"]) / summary["price_this_month"] *100
).round(1)
summary = summary.dropna().sort_values("change_pct", ascending=False)

prompt = f"""Here are average forecast prices per commodity in the Philippines (PHP).
change_pct is the change from this month to two months from now.

{summary.head(10).to_string(index=False)}

Explain the main trends in simple terms.
    """

try:
    for m in client.models.list().data:
        print(m.id)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "You are a careful price analyst. Use only the numbers "
                        "provided. Do not invent causes or data. These are "
                        "forecasts, not facts."},
            {"role": "user", 
             "content": prompt} 
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("LLM error:", e)

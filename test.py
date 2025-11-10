import pandas as pd
import aiohttp
import asyncio
import re
import os
from tqdm.asyncio import tqdm_asyncio

API_URL = "https://rec-engine.onrender.com/recommend"
OUT_CSV = "test.csv"


def extract_urls_from_text(text: str) -> list[str]:
    """Extract all URLs from a plain text string."""
    return re.findall(r"https?://[^\s\"'<>]+", text or "")


async def fetch_recommendations(session: aiohttp.ClientSession, query: str) -> list[str]:
    """Fetch URLs from API — supports both JSON and plain text responses."""
    try:
        async with session.post(API_URL, json={"query": query}, timeout=60) as resp:
            if resp.status != 200:
                print(f"[ERROR] {resp.status} for query: {query[:60]}")
                return []

            try:
                data = await resp.json(content_type=None)
                if isinstance(data, dict) and "recommended_assessments" in data:
                    return [r["url"].strip("/") for r in data["recommended_assessments"] if "url" in r]
                elif isinstance(data, str):
                    return extract_urls_from_text(data)
            except Exception:
                text = await resp.text()
                return extract_urls_from_text(text)
    except Exception as e:
        print(f"[EXCEPTION] Failed for query: {query[:60]} -> {e}")
        return []


async def generate_test_csv(excel_path: str, out_csv: str = OUT_CSV):
    """Read the test sheet, create CSV, and append rows as queries are processed."""
    xl = pd.ExcelFile(excel_path)
    df_test = xl.parse(xl.sheet_names[1])  # read second sheet (test set)
    df_test = df_test.dropna(subset=["Query"])
    queries = df_test["Query"].unique().tolist()

    # Create an empty CSV file with headers first
    pd.DataFrame(columns=["Query", "Assessment_url"]).to_csv(out_csv, index=False)
    print(f"Created empty CSV: {os.path.abspath(out_csv)}")

    async with aiohttp.ClientSession() as session:
        for query in tqdm_asyncio(queries, desc="Fetching test recommendations"):
            urls = await fetch_recommendations(session, query)
            rows = [{"Query": query, "Assessment_url": url} for url in urls]

            if rows:
                pd.DataFrame(rows).to_csv(out_csv, mode="a", header=False, index=False)

    print(f"\nAll results saved to {os.path.abspath(out_csv)}")


if __name__ == "__main__":
    asyncio.run(generate_test_csv("groundTruth.xlsx"))

import requests
from bs4 import BeautifulSoup

WAYBACK_API = "https://archive.org/wayback/available"

def fetch_snapshot(url, year):
    params = {
        "url": url,
        "timestamp": f"{year}0101"
    }
    r = requests.get(WAYBACK_API, params=params, timeout=10)
    data = r.json()
    snapshot = data.get("archived_snapshots", {}).get("closest")
    if not snapshot:
        return None

    snap_url = snapshot["url"]
    html = requests.get(snap_url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def compare_years(url, years):
    texts = {}
    for y in years:
        txt = fetch_snapshot(url, y)
        if txt:
            texts[y] = txt

    if len(texts) < 2:
        return {"success": False, "error": "Not enough historical data"}

    earliest, latest = sorted(texts.keys())[0], sorted(texts.keys())[-1]

    early_words = set(texts[earliest].lower().split())
    late_words = set(texts[latest].lower().split())

    gained = list(late_words - early_words)[:30]
    lost = list(early_words - late_words)[:30]

    return {
        "success": True,
        "earliest": earliest,
        "latest": latest,
        "new_focus_terms": gained,
        "deprecated_terms": lost
    }

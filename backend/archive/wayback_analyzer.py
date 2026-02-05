import requests
from bs4 import BeautifulSoup
import re

WAYBACK_API = "https://archive.org/wayback/available"


class WaybackAnalyzer:
    """
    Fetches and compares historical snapshots of a webpage
    using the Internet Archive (Wayback Machine).
    """

    def __init__(self, url: str):
        self.url = url

    def _fetch_snapshot_url(self, year: int):
        params = {
            "url": self.url,
            "timestamp": f"{year}0101"
        }
        resp = requests.get(WAYBACK_API, params=params, timeout=10)
        data = resp.json()

        snapshot = data.get("archived_snapshots", {}).get("closest")
        if snapshot and snapshot.get("available"):
            return snapshot["url"]
        return None

    def _extract_text(self, snapshot_url: str):
        html = requests.get(snapshot_url, timeout=10).text
        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "aside", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text)
        return text.lower()

    def analyze(self, years):
        texts = {}

        for year in years:
            snap_url = self._fetch_snapshot_url(year)
            if snap_url:
                texts[year] = self._extract_text(snap_url)

        if len(texts) < 2:
            return {
                "success": False,
                "error": "Not enough historical snapshots available"
            }

        sorted_years = sorted(texts.keys())
        old_year, new_year = sorted_years[0], sorted_years[-1]

        old_words = set(texts[old_year].split())
        new_words = set(texts[new_year].split())

        gained = sorted(list(new_words - old_words))[:40]
        lost = sorted(list(old_words - new_words))[:40]

        return {
            "success": True,
            "from_year": old_year,
            "to_year": new_year,
            "new_focus_terms": gained,
            "deprecated_terms": lost
        }

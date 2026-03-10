import requests
from collections import Counter
from bs4 import BeautifulSoup
import re


class WaybackAnalyzer:

    CDX_API = "https://web.archive.org/cdx/search/cdx"

    def __init__(self, url):

        url = url.strip()

        if not url.startswith("http"):
            url = "https://" + url

        if not url.endswith("/"):
            url = url + "/"

        self.url = url


    # --------------------------------------------------
    # Get closest snapshot to requested year
    # --------------------------------------------------
    def get_snapshot_for_year(self, year):

        try:

            params = {
                "url": self.url,
                "matchType": "prefix",
                "output": "json",
                "fl": "timestamp,original,statuscode",
                "filter": "statuscode:200",
                "limit": 200
            }

            r = requests.get(self.CDX_API, params=params, timeout=20)

            if r.status_code != 200:
                return None

            data = r.json()

            if len(data) <= 1:
                return None

            rows = data[1:]

            closest_timestamp = None
            closest_diff = 9999

            for row in rows:

                timestamp = row[0]
                snap_year = int(timestamp[:4])

                diff = abs(snap_year - year)

                if diff < closest_diff:
                    closest_diff = diff
                    closest_timestamp = timestamp

            if not closest_timestamp:
                return None

            archive_url = f"https://web.archive.org/web/{closest_timestamp}/{self.url}"

            return archive_url

        except Exception:
            return None


    # --------------------------------------------------
    # Fetch archived HTML text
    # --------------------------------------------------
    def fetch_text(self, archive_url):

        try:

            r = requests.get(archive_url, timeout=20)

            if r.status_code != 200:
                return ""

            soup = BeautifulSoup(r.text, "lxml")

            # 1. Decompose unwanted generic tags
            for tag in soup([
                "script", "style", "noscript", "header", "footer", "nav",
                "aside", "form", "button", "iframe", "svg", "video"
            ]):
                tag.decompose()

            # 2. Decompose common navigation/UI elements by class/id
            unwanted_selectors = [
                ".nav", ".navbar", ".menu", ".sidebar", ".footer", ".header",
                "#nav", "#navbar", "#menu", "#sidebar", "#footer", "#header",
                ".social", ".cookie", ".popup", ".modal", ".country-selector",
                ".language-picker", ".breadcrumb"
            ]
            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()

            # 3. Prefer <main> or <body>
            target_content = soup.find("main") or soup.find("body") or soup
            
            text = target_content.get_text(" ", strip=True)

            text = re.sub(r"\s+", " ", text)

            return text[:25000]

        except Exception:
            return ""


    # --------------------------------------------------
    # Extract keywords
    # --------------------------------------------------
    def extract_keywords(self, text):

        words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())

        stop_words = {
            "about","which","their","there","these","those","other","where",
            "while","could","would","should","before","after","because",
            "through","between","during","under","above","again","further",
            "being","having","every","against","within","without","among",
            "since","until","whose","website","internet","archive",
            "privacy","policy","copyright","terms","cookies","visit",
            "world","country","language","english","global","region",
            "italy","france","germany","spain","sweden","finland","denmark",
            "korea","japan","china","india","singapore",
            "search","login","account","store","support","customer",
            "contact","home","navigation","toggle","menu","explore","select",
            "follow","twitter","facebook","instagram","linkedin","youtube",
            "rights","reserved","content","skip","main","close","open",
            "https","applecom","apple","site","page","newsletter","subscribe"
        }

        filtered = [w for w in words if w not in stop_words]

        counter = Counter(filtered)

        return counter


    # --------------------------------------------------
    # Historical comparison
    # --------------------------------------------------
    def analyze(self, years):

        snapshots = {}

        for y in years:

            snap = self.get_snapshot_for_year(y)

            if not snap:
                continue

            text = self.fetch_text(snap)

            if not text:
                continue
            
            # Pre-extract keywords for each snapshot
            keywords = self.extract_keywords(text)

            snapshots[y] = {
                "url": snap,
                "text": text,
                "keywords": keywords
            }

        if len(snapshots) < 2:
            return {
                "success": False,
                "error": "Not enough historical snapshots available"
            }

        years_sorted = sorted(snapshots.keys())

        old_year = years_sorted[0]
        new_year = years_sorted[-1]

        old_words = snapshots[old_year]["keywords"]
        new_words = snapshots[new_year]["keywords"]

        top_old = dict(old_words.most_common(50))
        top_new = dict(new_words.most_common(50))

        emerging = []
        declining = []

        all_keys = set(top_old.keys()).union(set(top_new.keys()))

        for word in all_keys:

            old_freq = top_old.get(word, 0)
            new_freq = top_new.get(word, 0)

            if new_freq > old_freq:
                emerging.append((word, new_freq - old_freq))

            if old_freq > new_freq:
                declining.append((word, old_freq - new_freq))

        emerging.sort(key=lambda x: x[1], reverse=True)
        declining.sort(key=lambda x: x[1], reverse=True)

        emerging_terms = [w[0] for w in emerging[:15]]
        declining_terms = [w[0] for w in declining[:15]]

        # Prepare timeline for top appearing terms across ALL selected years
        timeline = {}

        timeline_words = list(set(list(top_old.keys())[:5] + list(top_new.keys())[:5]))

        for word in timeline_words:
            timeline[word] = {}
            for y in years_sorted:
                timeline[word][y] = snapshots[y]["keywords"].get(word, 0)

        return {

            "success": True,

            "from_year": old_year,
            "to_year": new_year,

            "from_url": snapshots[old_year]["url"],
            "to_url": snapshots[new_year]["url"],

            "from_text": snapshots[old_year]["text"],
            "to_text": snapshots[new_year]["text"],

            "new_focus_terms": emerging_terms,
            "deprecated_terms": declining_terms,

            "top_old_keywords": top_old,
            "top_new_keywords": top_new,

            "timeline_keywords": timeline,
            
            "all_years": years_sorted
        }

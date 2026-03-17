import requests
from collections import Counter
import re
from backend.archive.wayback_fetcher import analyze_historical_snapshots
from backend.archive.keyword_cleaner import clean_keywords
from backend.archive.domain_keywords import score_keywords
from backend.archive.domain_filters import filter_keywords

class WaybackAnalyzer:

    def __init__(self, url):
        url = url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        if not url.endswith("/"):
            url = url + "/"
        self.url = url

    # --------------------------------------------------
    # Detect Domain (Weighted Scoring)
    # --------------------------------------------------
    def detect_domain(self, text):
        text_lower = text.lower()
        words = text_lower.split()
        
        sports_keys = {"running","training","nike","basketball","tennis","performance","sports","athletic"}
        fashion_keys = {"fashion","denim","jacket","collection","style","clothing","wear","apparel"}
        ecommerce_keys = {"sale","discount","cart","shop","checkout","bestseller","offer"}
        news_keys = {"breaking","news","report","journal","article","headlines"}
        
        scores = {
            "sports": sum(1 for w in words if w in sports_keys),
            "fashion": sum(1 for w in words if w in fashion_keys),
            "ecommerce": sum(1 for w in words if w in ecommerce_keys),
            "news": sum(1 for w in words if w in news_keys)
        }
        
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] == 0:
            return "marketing"
            
        return best_domain
        
    # --------------------------------------------------
    # Trend Insight Generator
    # --------------------------------------------------
    def generate_trend_summary(self, emerging, declining, domain):
        """Rule-based insight generation substituting LLM with formatted sentences"""
        domain = domain.lower()
        
        emerging_str = ", ".join([w.title() for w in emerging[:3]]) if emerging else "various organic content"
        declining_str = ", ".join([w.title() for w in declining[:3]]) if declining else "general navigation features"
        
        if domain == "sports":
            return f"Analysis indicates growing emphasis on {emerging_str} products, while {declining_str} and general informational content has reduced over this timeframe."
            
        elif domain == "fashion":
            return f"Recent snapshots highlight increasing focus on {emerging_str} styles and lookbook-driven presentation, while previously tracked {declining_str} placements have diminished."
            
        elif domain == "ecommerce":
            return f"Historical website snapshots reveal a strategic shift toward highlighting {emerging_str} offers, effectively minimizing older {declining_str} layouts."
            
        elif domain == "news":
            return f"The data shows a structured evolution prioritizing {emerging_str} reporting categories, whereas historical {declining_str} sections appear significantly less prominent."
            
        else:
            return f"Market research highlights an organizational shift emphasizing {emerging_str} visibility, replacing earlier focus points like {declining_str} across the platform."

    # --------------------------------------------------
    # Extract keywords
    # --------------------------------------------------
    def extract_keywords(self, text, domain_mode="auto"):
        # 1) Tokenize text & lowercase
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        # 2) Clean keywords (stopwords, UI noise, length, digits)
        cleaned_words = clean_keywords(words)
        
        # Count frequencies
        counter = Counter(cleaned_words)
        word_freqs = dict(counter)

        # 3) Detect Domain if Auto
        if domain_mode == "auto" or domain_mode == "Auto":
            active_domain = self.detect_domain(text)
        else:
            active_domain = domain_mode
            
        # 4) Filter vocabulary (domain dictionary OR > 5 occurrences)
        filtered_freqs = filter_keywords(word_freqs, active_domain)

        # 5) Apply domain boosting
        scored_freqs = score_keywords(filtered_freqs, active_domain)

        # 6) Keep TOP 20 keywords
        sorted_keywords = sorted(scored_freqs.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Return format: [{"word": w, "score": s}, ...]
        return [{"word": w, "score": s} for w, s in sorted_keywords]

    # --------------------------------------------------
    # Trend Evolution Engine
    # --------------------------------------------------
    def compute_trends(self, snapshots, years_sorted):
        old_year = years_sorted[0]
        new_year = years_sorted[-1]
        
        old_keywords = {k["word"]: k["score"] for k in snapshots[old_year]["keywords"]}
        new_keywords = {k["word"]: k["score"] for k in snapshots[new_year]["keywords"]}
        
        all_words = set(old_keywords.keys()).union(set(new_keywords.keys()))
        
        emerging = []
        declining = []
        
        for word in all_words:
            old_freq = old_keywords.get(word, 0)
            new_freq = new_keywords.get(word, 0)
            
            delta = new_freq - old_freq
            
            if delta > 0:
                emerging.append({"word": word, "delta": delta})
            elif delta < 0:
                declining.append({"word": word, "delta": delta})
                
        # Sort and take top 10
        emerging.sort(key=lambda x: x["delta"], reverse=True)
        declining.sort(key=lambda x: abs(x["delta"]), reverse=True)
        
        return {
            "emerging": [w["word"] for w in emerging[:10]],
            "declining": [w["word"] for w in declining[:10]]
        }

    # --------------------------------------------------
    # Historical comparison
    # --------------------------------------------------
    def analyze(self, years, domain_mode="auto"):
        
        # 1) call get_wayback_snapshots() via our new pipeline
        fetcher_results = analyze_historical_snapshots(self.url, years)

        snapshots = {}

        for y, data in fetcher_results.items():
            text = data["content"]
            if not text:
                continue
            
            # Extract keywords via new pipeline
            keywords_list = self.extract_keywords(text, domain_mode)

            snapshots[y] = {
                "url": data["snapshot_url"],
                "text": text,
                "keywords": keywords_list
            }

        # Minimum 2 snapshots required
        if len(snapshots) < 2:
            return {
                "success": False,
                "error": "Not enough historical snapshots available"
            }
            
        warning = None
        if len(snapshots) < len(years):
            warning = f"Warning: Only found {len(snapshots)} out of {len(years)} requested snapshots."

        years_sorted = sorted(snapshots.keys())
        
        trends = self.compute_trends(snapshots, years_sorted)
        
        old_year = years_sorted[0]
        new_year = years_sorted[-1]
        
        top_old = {k["word"]: k["score"] for k in snapshots[old_year]["keywords"]}
        top_new = {k["word"]: k["score"] for k in snapshots[new_year]["keywords"]}

        # Prepare timeline for top appearing terms across ALL selected years
        timeline = {}
        timeline_words = list(set(list(top_old.keys())[:5] + list(top_new.keys())[:5]))

        for word in timeline_words:
            timeline[word] = {}
            for y in years_sorted:
                # Find score for this word in year y
                word_score = 0
                for kw in snapshots[y]["keywords"]:
                    if kw["word"] == word:
                        word_score = kw["score"]
                        break
                timeline[word][y] = word_score

        return {
            "success": True,
            "warning": warning,
            "from_year": old_year,
            "to_year": new_year,
            "from_url": snapshots[old_year]["url"],
            "to_url": snapshots[new_year]["url"],
            "from_text": snapshots[old_year]["text"],
            "to_text": snapshots[new_year]["text"],
            "new_focus_terms": trends["emerging"],
            "deprecated_terms": trends["declining"],
            "top_old_keywords": top_old,
            "top_new_keywords": top_new,
            "timeline_keywords": timeline,
            "all_years": years_sorted,
            "snapshots_data": snapshots # passing full format just in case
        }

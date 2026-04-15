import re
from collections import Counter
from typing import Dict


class DomainRouter:
    """
    Detect a website's domain category via keyword frequency analysis
    and return domain-specific extraction configuration.
    """

    # At least 10 keywords per domain for detection
    DOMAIN_KEYWORDS = {
        "marketing": [
            "seo", "campaign", "branding", "engagement", "conversion",
            "audience", "funnel", "analytics", "impressions", "ctr",
            "roi", "retargeting", "lead", "content marketing", "social media",
        ],
        "finance": [
            "stock", "portfolio", "investment", "revenue", "dividend",
            "equity", "bond", "interest rate", "inflation", "market cap",
            "earnings", "fiscal", "mutual fund", "banking", "credit",
        ],
        "ecommerce": [
            "cart", "checkout", "product", "price", "discount",
            "shipping", "order", "wishlist", "catalog", "inventory",
            "sku", "add to cart", "buy now", "payment", "refund",
        ],
        "news": [
            "breaking", "headline", "reporter", "editor", "press",
            "article", "coverage", "journalist", "exclusive", "source",
            "bulletin", "correspondent", "editorial", "byline", "newsroom",
        ],
        "sports": [
            "score", "match", "tournament", "championship", "athlete",
            "stadium", "league", "fixture", "goal", "team",
            "playoff", "coach", "season", "victory", "medal",
        ],
    }

    DOMAIN_CONFIGS: Dict[str, Dict] = {
        "marketing": {
            "focus_keywords": [
                "seo", "campaign", "branding", "engagement", "conversion",
                "funnel", "analytics", "roi", "lead generation", "growth",
            ],
            "ignore_keywords": [
                "cookie", "privacy policy", "terms of service", "footer",
            ],
            "extraction_hints": (
                "Focus on marketing metrics, campaign descriptions, "
                "audience segments, and conversion data."
            ),
        },
        "finance": {
            "focus_keywords": [
                "stock", "portfolio", "revenue", "earnings", "dividend",
                "market cap", "interest rate", "profit", "loss", "valuation",
            ],
            "ignore_keywords": [
                "advertisement", "cookie", "disclaimer", "terms",
            ],
            "extraction_hints": (
                "Focus on financial metrics, stock data, earnings reports, "
                "and investment analysis."
            ),
        },
        "ecommerce": {
            "focus_keywords": [
                "product", "price", "discount", "review", "rating",
                "shipping", "availability", "brand", "category", "deal",
            ],
            "ignore_keywords": [
                "cookie policy", "footer", "newsletter signup", "social links",
            ],
            "extraction_hints": (
                "Focus on product listings, prices, reviews, ratings, "
                "and availability information."
            ),
        },
        "news": {
            "focus_keywords": [
                "headline", "article", "reporter", "source", "breaking",
                "update", "exclusive", "opinion", "analysis", "investigation",
            ],
            "ignore_keywords": [
                "advertisement", "sponsored", "cookie", "subscribe popup",
            ],
            "extraction_hints": (
                "Focus on article content, headlines, dates, authors, "
                "and quoted sources."
            ),
        },
        "sports": {
            "focus_keywords": [
                "score", "match", "team", "player", "tournament",
                "championship", "league", "standings", "result", "fixture",
            ],
            "ignore_keywords": [
                "advertisement", "cookie", "fantasy league signup", "newsletter",
            ],
            "extraction_hints": (
                "Focus on scores, match results, player statistics, "
                "and tournament standings."
            ),
        },
        "general": {
            "focus_keywords": [
                "about", "services", "contact", "information", "overview",
                "features", "solutions", "team", "mission", "resources",
            ],
            "ignore_keywords": [
                "cookie", "footer", "privacy", "terms",
            ],
            "extraction_hints": (
                "Extract main content sections, key topics, "
                "and any structured data available."
            ),
        },
    }

    # -------------------------------------------------------
    # Detection
    # -------------------------------------------------------
    def detect_domain(self, content: str, url: str) -> str:
        """
        Detect the domain category from content + URL via keyword
        frequency analysis. Returns one of: marketing, finance,
        ecommerce, news, sports, general.
        """
        text = (content + " " + url).lower()
        words = re.findall(r"\w+", text)
        word_counts = Counter(words)

        scores: Dict[str, int] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Support multi-word keywords
                if " " in kw:
                    score += text.count(kw)
                else:
                    score += word_counts.get(kw, 0)
            scores[domain] = score

        if not scores or max(scores.values()) == 0:
            return "general"

        best = max(scores, key=scores.get)
        return best

    # -------------------------------------------------------
    # Config
    # -------------------------------------------------------
    def get_domain_config(self, domain: str) -> Dict:
        """
        Return domain-specific extraction configuration.
        Keys: focus_keywords, ignore_keywords, extraction_hints.
        """
        return self.DOMAIN_CONFIGS.get(domain, self.DOMAIN_CONFIGS["general"])


# ---------------------------------------------------------
# Backward-compatible module-level helper (used by existing code)
# ---------------------------------------------------------
def detect_domain(url: str) -> str:
    """Legacy helper — kept for backward compatibility."""
    router = DomainRouter()
    return router.detect_domain("", url)

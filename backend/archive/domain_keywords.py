DOMAIN_VOCABS = {
    "marketing": {
        "words": ["collection", "campaign", "trend", "style", "look", "season", "launch"],
        "weight": 2
    },
    "fashion": {
        "words": ["jacket", "denim", "hoodie", "oversized", "cargo", "sneakers", "athleisure", "winter", "summer", "wear", "clothing", "apparel", "fit"],
        "weight": 2
    },
    "ecommerce": {
        "words": ["sale", "discount", "offer", "new arrivals", "trending", "bestseller", "shop", "buy", "price", "checkout"],
        "weight": 2
    },
    "sports": {
        "words": ["running", "training", "performance", "air", "zoom", "react", "sport", "athletic", "gear", "equipment"],
        "weight": 2
    },
    "finance": {
        "words": ["stock", "revenue", "invest", "market", "trading", "portfolio", "wealth", "finance", "capital", "equity"],
        "weight": 2
    },
    "news": {
        "words": ["breaking", "latest", "update", "report", "article", "headlines", "politics", "world", "local"],
        "weight": 2
    }
}

def score_keywords(word_frequencies: dict, domain: str) -> dict:
    """
    Boost relevant words by their specified weight based on domain.
    Mode 'auto' will not boost anything directly here (handled by detection upstream if desired).
    """
    domain = domain.lower()
    if domain not in DOMAIN_VOCABS:
        return word_frequencies

    boost_words = set(DOMAIN_VOCABS[domain]["words"])
    boost_weight = DOMAIN_VOCABS[domain]["weight"]

    scored = {}
    for word, count in word_frequencies.items():
        if word in boost_words:
            scored[word] = count + boost_weight
        else:
            scored[word] = count

    return scored

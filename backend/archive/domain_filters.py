DOMAIN_FILTERS = {
    "fashion": [
        "denim","jacket","hoodie","oversized","streetwear","winter","summer",
        "collection","lookbook","style","fashion"
    ],
    "sports": [
        "running","training","basketball","tennis","performance","zoom","react",
        "air","nike","jordan","athletic","sneakers"
    ],
    "ecommerce": [
        "sale","discount","offer","trending","bestseller","shopping","fashion","electronics"
    ],
    "news": [
        "breaking","report","global","policy","analysis","journal"
    ]
}

GLOBAL_STOPWORDS = {
    "shop", "store", "home", "with", "more", "your", "kids", "men", "women",
    "search", "menu", "cart", "account", "login", "signup"
}

def filter_keywords(word_frequencies: dict, domain: str) -> dict:
    """
    IF word in domain list: keep
    ELIF freq > 5 AND word not in global stopwords: keep
    ELSE: discard
    FALLBACK: If < 5 keywords remain, use top frequencies regardless.
    """
    domain = domain.lower()
    
    # Auto logic or undefined domains pass through > 5 times filter unconditionally.
    if domain not in DOMAIN_FILTERS:
        allowed_vocab = set()
    else:
        allowed_vocab = set(DOMAIN_FILTERS[domain])

    filtered = {}
    
    for word, count in word_frequencies.items():
        if word in allowed_vocab:
            filtered[word] = count
        elif count > 5 and word not in GLOBAL_STOPWORDS:
            filtered[word] = count

    # Minimum keyword guarantee fallback (if < 5 extracted keywords)
    if len(filtered) < 5:
        # Sort original words by frequency and pick top 10 not in global stopwords
        top_words = sorted(
            [(w, c) for w, c in word_frequencies.items() if w not in GLOBAL_STOPWORDS],
            key=lambda x: x[1], reverse=True
        )
        for w, c in top_words[:10]:
            filtered[w] = c

    return filtered

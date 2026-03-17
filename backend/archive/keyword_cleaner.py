def clean_keywords(words: list[str]) -> list[str]:
    """Filters noise, short words, numbers, and common web stopwords."""
    
    stop_words = {
        # Generic web words
        "login", "signup", "home", "menu", "search", "cart", "account",
        "about", "contact", "support", "visit", "explore", "select", 
        "language", "country", "region", "global", "newsletter", "subscribe",
        "store", "customer", "site", "page", "website", "internet",

        # UI & action words
        "click", "accept", "allow", "settings", "preferences", "close", "open",
        "toggle", "skip", "main", "follow", "rights", "reserved", "content",

        # Navigation terms
        "back", "next", "previous", "return", "forward",

        # General English stopwords
        "which", "their", "there", "these", "those", "other", "where",
        "while", "could", "would", "should", "before", "after", "because",
        "through", "between", "during", "under", "above", "again", "further",
        "being", "having", "every", "against", "within", "without", "among",
        "since", "until", "whose", "privacy", "policy", "copyright", "terms",
        "cookies", "world", "english", "italy", "france", "germany", "spain",
        "sweden", "finland", "denmark", "korea", "japan", "china", "india",
        "singapore", "twitter", "facebook", "instagram", "linkedin", "youtube",
        "applecom", "apple", "https", "http", "www"
    }

    cleaned = []
    for word in words:
        w = word.lower().strip()
        # Remove short words (<4 chars)
        if len(w) < 4:
            continue
        # Remove numeric tokens completely
        if w.isnumeric() or any(char.isdigit() for char in w):
            continue
        # Remove stopwords
        if w in stop_words:
            continue
            
        cleaned.append(w)
        
    return cleaned

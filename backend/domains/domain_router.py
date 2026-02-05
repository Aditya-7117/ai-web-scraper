def detect_domain(url):
    if "magicbricks" in url:
        return "real_estate"
    if "amazon" in url or "flipkart" in url:
        return "ecommerce"
    if "news" in url:
        return "news"
    return "generic"

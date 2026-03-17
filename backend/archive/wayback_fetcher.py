import requests
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CDX_API = "https://web.archive.org/cdx/search/cdx"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118 Safari/537.36"
]

def get_wayback_snapshots(domain: str, years: list[int]) -> dict:
    params = {
        "url": domain,
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
        "collapse": "timestamp:8"
    }
    
    try:
        r = requests.get(CDX_API, params=params, timeout=30)
        if r.status_code != 200:
            return {}
        data = r.json()
    except Exception:
        return {}
        
    if len(data) <= 1:
        return {}
        
    rows = data[1:]
    
    # Group by year
    snapshots_by_year = {}
    for row in rows:
        timestamp = row[0]
        original_url = row[1]
        
        if len(timestamp) < 6:
            continue
            
        snap_year = int(timestamp[:4])
        snap_month = int(timestamp[4:6])
        
        if snap_year not in snapshots_by_year:
            snapshots_by_year[snap_year] = []
            
        snapshots_by_year[snap_year].append({
            "timestamp": timestamp,
            "original": original_url,
            "month": snap_month
        })
        
    results = {}
    
    for req_year in years:
        target_year = None
        
        # Check current year
        if req_year in snapshots_by_year:
            target_year = req_year
        else:
            # Fallback +/- 2 years logic: find nearest available
            closest_diff = 999
            for diff in [1, -1, 2, -2]:
                fallback_year = req_year + diff
                if fallback_year in snapshots_by_year:
                    if abs(diff) < closest_diff:
                        closest_diff = abs(diff)
                        target_year = fallback_year
                        
        if target_year:
            # Pick best snapshot (closest to June)
            best_snap = None
            min_dist = 999
            for snap in snapshots_by_year[target_year]:
                dist = abs(snap["month"] - 6)
                if dist < min_dist:
                    min_dist = dist
                    best_snap = snap
                    
            if best_snap:
                ts = best_snap["timestamp"]
                snap_url = f"https://web.archive.org/web/{ts}/{domain}"
                results[req_year] = {
                    "timestamp": ts,
                    "snapshot_url": snap_url
                }
                
    return results

def setup_stealth_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    
    # Randomize user agent and window size
    ua = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={ua}")
    
    widths = [1366, 1440, 1920, 2560]
    heights = [768, 900, 1080, 1440]
    w = random.choice(widths)
    h = random.choice(heights)
    chrome_options.add_argument(f"--window-size={w},{h}")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Add JS script to mask webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def fetch_snapshot_html(snapshot_url: str) -> str:
    # Try requests first
    for attempt in range(3):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            r = requests.get(snapshot_url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        time.sleep(1)
        
    # Fallback to Selenium Stealth
    driver = None
    try:
        driver = setup_stealth_driver()
        driver.get(snapshot_url)
        time.sleep(3) # Wait for page load
        html = driver.page_source
        return html
    except Exception:
        return ""
    finally:
        if driver:
            driver.quit()

def clean_archive_html(html: str) -> str:
    if not html:
        return ""
        
    soup = BeautifulSoup(html, "lxml")
    
    # Remove archive banners
    for tag in soup(id="wm-ipp"):
        tag.decompose()
    for tag in soup(class_="wm-ipp"):
        tag.decompose()
        
    # Remove standard tags
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()
        
    text = soup.get_text(separator=" ", strip=True)
    import re
    text = re.sub(r"\s+", " ", text).strip()
    return text

def analyze_historical_snapshots(domain: str, years: list[int]) -> dict:
    snapshots = get_wayback_snapshots(domain, years)
    
    results = {}
    count = len(snapshots)
    print(f"[WAYBACK] snapshots found: {count}")
    
    for y, info in snapshots.items():
        ts = info["timestamp"]
        url = info["snapshot_url"]
        
        print(f"[WAYBACK] using snapshot: {ts}")
        
        html = fetch_snapshot_html(url)
        clean_ext = clean_archive_html(html)
        
        words = len(clean_ext.split())
        
        results[y] = {
            "snapshot_url": url,
            "content": clean_ext,
            "word_count": words
        }
        
    return results

import requests

CDX_API = "https://web.archive.org/cdx/search/cdx"

def find_archive_compatible_sites(domains: list[str]) -> list[dict]:
    """
    Checks each domain against Wayback Machine CDX API.
    Returns domains having >200 snapshots and >5 years of history.
    """
    compatible_sites = []
    
    # Limit to max 10 domains per run
    processed = 0
    
    for domain in domains:
        if processed >= 10:
            break
            
        print("Checking:", domain)
        processed += 1
        
        params = {
            "url": domain,
            "output": "json",
            "filter": "statuscode:200",
            "fl": "timestamp"
        }
        
        try:
            # 5s timeout
            r = requests.get(CDX_API, params=params, timeout=5)
            if r.status_code != 200:
                continue
                
            data = r.json()
            if len(data) <= 1:
                continue
                
            rows = data[1:] # Skip header
            
            snapshot_count = len(rows)
            
            # Find history range
            years = []
            for row in rows:
                ts = row[0]
                if len(ts) >= 4:
                    years.append(int(ts[:4]))
                    
            if not years:
                continue
                
            first_year = min(years)
            last_year = max(years)
            history = last_year - first_year
            
            if snapshot_count > 200 and history > 5:
                compatible_sites.append({
                    "domain": domain,
                    "snapshot_count": snapshot_count,
                    "first_year": first_year,
                    "last_year": last_year,
                    "history_years": history
                })
                
                # Early stopping: 5 valid domains found
                if len(compatible_sites) >= 5:
                    break
                
        except Exception:
            pass
            
    # Sort by snapshot count descending
    compatible_sites.sort(key=lambda x: x["snapshot_count"], reverse=True)
    return compatible_sites

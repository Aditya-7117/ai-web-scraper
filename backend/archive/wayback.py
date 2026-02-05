import requests

WAYBACK_API = "https://archive.org/wayback/available"

def fetch_snapshot(url, year):
    params = {"url": url, "timestamp": f"{year}0101"}
    r = requests.get(WAYBACK_API, params=params, timeout=10)
    data = r.json()
    snapshots = data.get("archived_snapshots", {})
    closest = snapshots.get("closest")
    return closest["url"] if closest else None

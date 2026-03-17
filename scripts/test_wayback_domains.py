import sys
import os

# Add project root to sys path to import backend modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.archive.demo_domains import ALL_DEMO_DOMAINS
from backend.archive.archive_tester import find_archive_compatible_sites

def main():
    print(f"Testing {len(ALL_DEMO_DOMAINS)} demo domains against CDX API...\n")
    
    compatible_domains = find_archive_compatible_sites(ALL_DEMO_DOMAINS)
    
    if not compatible_domains:
        print("No compatible domains found.")
        return
        
    print("Compatible Wayback Sites:\n")
    for site in compatible_domains:
        domain = site["domain"]
        count = site["snapshot_count"]
        # Format snapshot count with commas
        count_formatted = f"{count:,}"
        print(f"{domain} — {count_formatted} snapshots")

if __name__ == "__main__":
    main()

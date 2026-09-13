import json
import os
import re
import urllib.request
from typing import Optional, Set

WHITELIST = {
    "localhost",
    "clients3.google.com",
    "s.youtube.com"
}

OUTPUT_DIR = "blocklists"
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)

def extract_domain(line: str) -> Optional[str]:
    line = line.strip()
    if not line or line.startswith(('#', '!')):
        return None
    if '^$' in line:
        line = line.split('^$', 1)[0]
    if line.endswith('^'):
        line = line[:-1]
    if line.startswith('||'):
        line = line[2:]
    if '/' in line or '*' in line:
        return None
    if ' ' in line or '\t' in line:
        parts = line.split()
        line = parts[-1]
    return line.lower()

def fetch_domains_from_urls(urls: list[str]) -> Set[str]:
    domains: Set[str] = set()
    headers = {'User-Agent': 'Mozilla/5.0 (BlocklistCompiler/4.0)'}

    for url in urls:
        print(f"  --> Fetching: {url}")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                for line_bytes in response:
                    try:
                        line = line_bytes.decode('utf-8', errors='ignore')
                    except Exception:
                        continue
                    
                    domain = extract_domain(line)
                    if domain and domain not in WHITELIST:
                        if DOMAIN_REGEX.match(domain):
                            domains.add(domain)
        except Exception as e:
            print(f"  [!] Failed {url}: {e}")

    return domains

def write_tier_file(filename: str, domains: Set[str], tier_name: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Blocklist Tier: {tier_name}\n")
        f.write(f"# Total Unique Domains: {len(domains)}\n\n")
        for domain in sorted(domains):
            f.write(f"0.0.0.0 {domain}\n")
    print(f"[+] Saved {tier_name} Tier ({len(domains):,} domains) -> {filepath}\n")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists("sources.json"):
        print("Error: sources.json not found.")
        return

    with open("sources.json", "r", encoding="utf-8") as f:
        sources_by_tier = json.load(f)

    # 1. Gather Basic
    print("=== Processing Basic Tier ===")
    basic_urls = [url for category in sources_by_tier.get("basic", {}).values() for url in category]
    basic_domains = fetch_domains_from_urls(basic_urls)
    write_tier_file("basic.txt", basic_domains, "Basic")

    # 2. Gather Balanced (Basic + Balanced)
    print("=== Processing Balanced Tier ===")
    balanced_urls = [url for category in sources_by_tier.get("balanced", {}).values() for url in category]
    balanced_domains = basic_domains.union(fetch_domains_from_urls(balanced_urls))
    write_tier_file("balanced.txt", balanced_domains, "Balanced")

    # 3. Gather Ultimate (Balanced + Ultimate)
    print("=== Processing Ultimate Tier ===")
    ultimate_urls = [url for category in sources_by_tier.get("ultimate", {}).values() for url in category]
    ultimate_domains = balanced_domains.union(fetch_domains_from_urls(ultimate_urls))
    write_tier_file("ultimate.txt", ultimate_domains, "Ultimate")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from typing import Optional, Set

OUTPUT_DIR = "blocklists"
CONFIG_DIR = "config"
WHITELIST_FILE = os.path.join(CONFIG_DIR, "build_whitelist.txt")

# Pre-compiled strict domain matcher
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)

# Hardcoded essential fallbacks in case config file is missing
DEFAULT_WHITELIST = {
    "localhost",
    "clients3.google.com",
    "s.youtube.com"
}


def load_whitelist() -> Set[str]:
    """Loads build-time whitelist domains from disk."""
    whitelist = set(DEFAULT_WHITELIST)
    
    # Check config/build_whitelist.txt first, fallback to root whitelist.txt
    target_file = WHITELIST_FILE if os.path.exists(WHITELIST_FILE) else "whitelist.txt"
    
    if os.path.exists(target_file):
        print(f"[+] Loading whitelist from: {target_file}")
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().lower()
                    if line and not line.startswith(('#', '!')):
                        # Strip inline comments or host prefixes if present
                        domain = line.split()[0].rstrip('^').lstrip('||')
                        if '/' not in domain and '*' not in domain:
                            whitelist.add(domain)
        except Exception as e:
            print(f"[!] Warning reading {target_file}: {e}")
    else:
        print("[!] No whitelist file found. Using default internal whitelist.")
        
    print(f"[+] Active Whitelist Count: {len(whitelist)} domains\n")
    return whitelist


def extract_domain(line: str) -> Optional[str]:
    """Extremely fast domain extractor bypassing heavy regex on dirty lines."""
    line = line.strip()
    
    # Fast drop empty or comment lines
    if not line or line.startswith(('#', '!')):
        return None

    # Remove AdBlock option modifiers (e.g., ^$third-party)
    if '^$' in line:
        line = line.split('^$', 1)[0]
    
    # Strip AdBlock wrapper syntax
    if line.endswith('^'):
        line = line[:-1]
    if line.startswith('||'):
        line = line[2:]

    # Path-based or wildcard rules cannot be resolved at DNS host level
    if '/' in line or '*' in line:
        return None

    # Extract domain if preceded by IP (e.g., 0.0.0.0 domain.com or 127.0.0.1 domain.com)
    if ' ' in line or '\t' in line:
        parts = line.split()
        line = parts[-1]

    return line.lower()


def fetch_domains_from_urls(urls: list[str], whitelist: Set[str]) -> Set[str]:
    """Streams data line-by-line to keep RAM usage minimal."""
    domains: Set[str] = set()
    headers = {'User-Agent': 'Mozilla/5.0 (BlocklistCompiler/5.0)'}

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
                    if domain and domain not in whitelist:
                        if DOMAIN_REGEX.match(domain):
                            domains.add(domain)
        except Exception as e:
            print(f"  [!] ERROR fetching {url}: {e}")

    return domains


def write_tier_file(filename: str, domains: Set[str], tier_name: str):
    """Outputs standard hosts file format."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Blocklist Tier: {tier_name}\n")
        f.write(f"# Total Unique Domains: {len(domains):,}\n\n")
        for domain in sorted(domains):
            f.write(f"0.0.0.0 {domain}\n")
    print(f"[+] Saved {tier_name} Tier ({len(domains):,} domains) -> {filepath}\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists("sources.json"):
        print("Error: sources.json file not found.")
        return

    # Load active whitelist entries
    whitelist = load_whitelist()

    with open("sources.json", "r", encoding="utf-8") as f:
        sources_by_tier = json.load(f)

    # 1. Gather Basic Tier
    print("=== Processing Basic Tier ===")
    basic_urls = [url for category in sources_by_tier.get("basic", {}).values() for url in category]
    basic_domains = fetch_domains_from_urls(basic_urls, whitelist)
    write_tier_file("basic.txt", basic_domains, "Basic")

    # 2. Gather Balanced Tier (Basic + Balanced)
    print("=== Processing Balanced Tier ===")
    balanced_urls = [url for category in sources_by_tier.get("balanced", {}).values() for url in category]
    balanced_domains = basic_domains.union(fetch_domains_from_urls(balanced_urls, whitelist))
    write_tier_file("balanced.txt", balanced_domains, "Balanced")

    # 3. Gather Ultimate Tier (Balanced + Ultimate)
    print("=== Processing Ultimate Tier ===")
    ultimate_urls = [url for category in sources_by_tier.get("ultimate", {}).values() for url in category]
    ultimate_domains = balanced_domains.union(fetch_domains_from_urls(ultimate_urls, whitelist))
    write_tier_file("ultimate.txt", ultimate_domains, "Ultimate")


if __name__ == "__main__":
    main()

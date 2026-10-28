#!/usr/bin/env python3
import hashlib
import ipaddress
import json
import os
import re
import urllib.error
import urllib.request
from datetime import UTC, datetime

OUTPUT_DIR = "blocklists"
WHITELIST_FILE = "whitelist.txt"
SUMMARY_FILE = "build_summary.md"

# Pre-compiled strict domain matcher
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)

DEFAULT_WHITELIST = {
    "localhost",
    "clients3.google.com",
    "s.youtube.com"
}


def get_version() -> str:
    """Retrieves version from BLOCKLIST_VERSION env var, or defaults to current UTC date tag."""
    return os.getenv("BLOCKLIST_VERSION", datetime.now(UTC).strftime("v%Y.%m.%d"))


def sanitize_domain_entry(line: str) -> str | None:
    """
    Strips inline comments, protocol prefixes, trailing slashes, 
    and adblock-style formatting rules to return a clean domain string.
    """
    line = line.strip()
    
    # Skip empty lines or full-line comments
    if not line or line.startswith(('#', '!', '//')):
        return None

    # Remove inline comments
    line = line.split('#')[0].split('!')[0].strip()

    # Strip protocols and common adblock rule prefixes/suffixes
    line = line.lower()
    line = re.sub(r'^https?://', '', line)
    line = line.removeprefix('||').removesuffix('^')

    # Remove paths or query parameters if present
    if '/' in line:
        line = line.split('/')[0]

    # Remove port numbers
    if ':' in line:
        line = line.split(':')[0]

    # Ignore wildcard entries or invalid characters
    if '*' in line or not line:
        return None

    return line if DOMAIN_REGEX.match(line) else None


def clean_and_deduplicate_whitelist_file(filepath: str):
    """
    Reads whitelist.txt, preserves header comments, cleans domains, 
    deduplicates entries, and rewrites the file sorted alphabetically.
    """
    if not os.path.exists(filepath):
        print(f"[!] Warning: Whitelist file '{filepath}' not found. Creating a new one.")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Community Whitelist\n\n")
            f.writelines(f"{domain}\n" for domain in sorted(DEFAULT_WHITELIST))
        return

    print(f"[+] Sanitizing and deduplicating whitelist file: {filepath}")
    
    valid_domains: set[str] = set()
    file_header_comments = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Preserve initial header comments at the top of the file
            if stripped.startswith(('#', '!')) and not valid_domains:
                file_header_comments.append(stripped)
                continue

            cleaned_domain = sanitize_domain_entry(line)
            if cleaned_domain:
                valid_domains.add(cleaned_domain)

    # Rewrite whitelist.txt with cleaned, sorted domains
    with open(filepath, "w", encoding="utf-8") as f:
        if file_header_comments:
            f.writelines(f"{comment}\n" for comment in file_header_comments)
            f.write("\n")
            
        f.writelines(f"{domain}\n" for domain in sorted(valid_domains))

    print(f"    ✔ Cleaned file written with {len(valid_domains):,} unique domains.")


def load_whitelist() -> set[str]:
    """Sanitizes root whitelist.txt and loads active whitelist domains into memory."""
    whitelist = set(DEFAULT_WHITELIST)
    
    # Sanitize and deduplicate root whitelist file on disk
    clean_and_deduplicate_whitelist_file(WHITELIST_FILE)

    # Read clean domains into memory
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            for line in f:
                domain = sanitize_domain_entry(line)
                if domain:
                    whitelist.add(domain)

    print(f"[+] Total Active Whitelist Count: {len(whitelist):,} domains\n")
    return whitelist


def extract_domains(line: str) -> set[str]:
    """Extract domains from hosts files and common adblock rule formats."""
    line = line.strip()

    if not line or line.startswith(('#', '!', '//')):
        return set()

    line = line.split('#', 1)[0].strip()
    if not line:
        return set()

    parts = line.split()
    try:
        ipaddress.ip_address(parts[0])
        candidates = parts[1:]
    except ValueError:
        candidates = parts

    domains = set()
    for candidate in candidates:
        if '^$' in candidate:
            candidate = candidate.split('^$', 1)[0]

        candidate = candidate.removeprefix('||').removesuffix('^')

        candidate = candidate.lower()
        if not any(char in candidate for char in '/*:') and DOMAIN_REGEX.fullmatch(candidate):
            domains.add(candidate)

    return domains


def fetch_domains_from_urls(urls: list[str], whitelist: set[str]) -> set[str]:
    """Streams data line-by-line to keep RAM usage minimal."""
    domains: set[str] = set()
    successful_sources = 0
    headers = {'User-Agent': 'Mozilla/5.0 (BlocklistCompiler/6.0)'}

    for url in urls:
        print(f"  --> Fetching: {url}")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                for line_bytes in response:
                    line = line_bytes.decode('utf-8', errors='ignore')
                    domains.update(extract_domains(line) - whitelist)
            successful_sources += 1
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                print(f"  [!] Skipping unavailable source (HTTP {e.code}): {url}")
                continue
            raise RuntimeError(f"Failed to fetch source {url}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to fetch source {url}: {e}") from e

    if successful_sources == 0:
        raise RuntimeError("No sources could be fetched.")

    return domains


def write_tier_file(filename: str, domains: set[str], tier_name: str):
    """Outputs standard hosts file format with version header."""
    filepath = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(filepath):
        existing_domains = set()
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) == 2 and parts[0] == "0.0.0.0":
                    existing_domains.add(parts[1])
        if existing_domains == domains:
            print(f"[+] No domain changes for {tier_name} Tier; keeping existing file.\n")
            return

    version = get_version()
    updated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Blocklist Tier: {tier_name}\n")
        f.write(f"# Version: {version}\n")
        f.write(f"# Updated: {updated_at}\n")
        f.write(f"# Total Unique Domains: {len(domains):,}\n\n")
        f.writelines(f"0.0.0.0 {domain}\n" for domain in sorted(domains))
    print(f"[+] Saved {tier_name} Tier ({len(domains):,} domains) -> {filepath}\n")


def generate_checksums():
    """Generates sha256sums.txt for compiled blocklist assets."""
    checksum_file = os.path.join(OUTPUT_DIR, "sha256sums.txt")
    files_to_hash = ["basic.txt", "balanced.txt", "ultimate.txt"]
    
    with open(checksum_file, "w", encoding="utf-8") as out:
        for fname in files_to_hash:
            fpath = os.path.join(OUTPUT_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, "rb") as f:
                    digest = hashlib.sha256(f.read()).hexdigest()
                out.write(f"{digest}  {fname}\n")
                
    print(f"[+] Generated SHA256 checksums -> {checksum_file}\n")


def generate_summary(counts: dict[str, int]):
    """Generates a concise release summary table."""
    version = get_version()
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(f"### Release {version}\n")
        f.write("Automated build of network protection tiers compiled from verified threat feeds.\n\n")
        f.write("| Protection Tier | File | Total Domains |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Basic** | `basic.txt` | `{counts.get('Basic', 0):,}` |\n")
        f.write(f"| **Balanced** | `balanced.txt` | `{counts.get('Balanced', 0):,}` |\n")
        f.write(f"| **Ultimate** | `ultimate.txt` | `{counts.get('Ultimate', 0):,}` |\n\n")
        f.write("--- \n")
        f.write("*Filtered against built-in false-positive whitelist rules. SHA256 checksums available in release assets.*")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists("sources.json"):
        print("Error: sources.json file not found.")
        return

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

    # 4. Generate Checksums
    generate_checksums()

    # 5. Generate Release Summary
    counts = {
        "Basic": len(basic_domains),
        "Balanced": len(balanced_domains),
        "Ultimate": len(ultimate_domains)
    }
    generate_summary(counts)


if __name__ == "__main__":
    main()

import json
import os
import re
import urllib.request
from typing import Optional, Set

# Whitelist set (O(1) lookup speed)
WHITELIST = {
    "localhost",
    "clients3.google.com",
    "s.youtube.com"
}

OUTPUT_DIR = "blocklists"

# Pre-compiled strict domain matcher
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)

def extract_domain(line: str) -> Optional[str]:
    """Extremely fast domain extractor bypassing heavy regex on dirty lines."""
    line = line.strip()
    
    # Fast drop empty or comment lines
    if not line or line.startswith('#') or line.startswith('!'):
        return None

    # Remove AdBlock option modifiers (e.g., ^$third-party)
    if '^$' in line:
        line = line.split('^$', 1)[0]
    
    # Strip AdBlock wrapper syntax
    if line.endswith('^'):
        line = line[:-1]
    if line.startswith('||'):
        line = line[2:]

    # Fast check: wildcard or path-based rules cannot be host blocked
    if '/' in line or '*' in line:
        return None

    # Extract domain if preceded by IP (e.g., 0.0.0.0 domain.com or 127.0.0.1 domain.com)
    if ' ' in line or '\t' in line:
        parts = line.split()
        line = parts[-1]

    possible_domain = line.lower()
    return possible_domain

def process_category(category: str, urls: list[str]) -> None:
    """Streams data line-by-line to keep RAM usage minimal."""
    entries: Set[str] = set()
    headers = {'User-Agent': 'Mozilla/5.0 (BlocklistCompiler/3.0)'}

    for url in urls:
        print(f"[{category}] Fetching: {url}")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                # Stream line-by-line using low-memory iterator
                for line_bytes in response:
                    try:
                        line = line_bytes.decode('utf-8', errors='ignore')
                    except Exception:
                        continue
                    
                    line = line.strip()
                    if not line or line.startswith(('#', '!')):
                        continue

                    # Special case: preserve raw lines for regex category
                    if category == "regex":
                        entries.add(line)
                        continue

                    domain = extract_domain(line)
                    if domain and domain not in WHITELIST:
                        if DOMAIN_REGEX.match(domain):
                            entries.add(domain)

        except Exception as e:
            print(f"[{category}] ERROR on {url}: {e}")

    # Write output to disk
    output_file = os.path.join(OUTPUT_DIR, f"{category}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Category: {category}\n# Total Unique Entries: {len(entries)}\n")
        if category == "regex":
            for entry in sorted(entries):
                f.write(f"{entry}\n")
        else:
            for domain in sorted(entries):
                f.write(f"0.0.0.0 {domain}\n")

    print(f"[{category}] Saved {len(entries):,} unique domains -> {output_file}\n")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists("sources.json"):
        print("Error: sources.json file not found.")
        return

    with open("sources.json", "r", encoding="utf-8") as f:
        categories = json.load(f)

    for category, urls in categories.items():
        process_category(category, urls)

if __name__ == "__main__":
    main()

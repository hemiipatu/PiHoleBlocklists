import json
import os
import re
import urllib.request

WHITELIST = {
    "localhost",
    "clients3.google.com",
    "s.youtube.com"
}

OUTPUT_DIR = "blocklists"

def extract_domain(line):
    line = line.strip()
    
    # Ignore blank lines and comments
    if not line or line.startswith(('#', '!')):
        return None
    
    # Strip AdBlock option modifiers (e.g., ^$third-party)
    if '^$' in line:
        line = line.split('^$')[0]
    
    # Trim AdBlock syntax
    line = line.rstrip('^')
    if line.startswith('||'):
        line = line[2:]
    
    # Trim host prefix IPs
    parts = line.split()
    possible_domain = parts[-1].lower()
    
    if '/' in possible_domain or '*' in possible_domain:
        return None
        
    return possible_domain

def process_category(category, urls):
    entries = set()
    domain_regex = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'BlocklistBuilder/2.0'})
            with urllib.request.urlopen(req) as response:
                lines = response.read().decode('utf-8', errors='ignore').splitlines()
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith(('#', '!')):
                        continue

                    # Special rule: Preserve raw regex pattern lines for regex.txt
                    if category == "regex":
                        entries.add(line)
                        continue

                    domain = extract_domain(line)
                    if domain and domain not in WHITELIST and domain_regex.match(domain):
                        entries.add(domain)
        except Exception as e:
            print(f"[{category}] Failed to process {url}: {e}")

    # Output file path
    output_file = os.path.join(OUTPUT_DIR, f"{category}.txt")
    with open(output_file, "w") as f:
        f.write(f"# Category: {category}\n# Total Unique Entries: {len(entries)}\n")
        for entry in sorted(entries):
            if category == "regex":
                f.write(f"{entry}\n")
            else:
                f.write(f"0.0.0.0 {entry}\n")

    print(f"Generated {output_file} ({len(entries)} entries)")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists("sources.json"):
        print("Error: sources.json file not found.")
        return

    with open("sources.json", "r") as f:
        categories = json.load(f)

    for category, urls in categories.items():
        process_category(category, urls)

if __name__ == "__main__":
    main()

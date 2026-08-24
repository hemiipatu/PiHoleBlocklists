#!/usr/bin/env bash
# Automatically imports all category blocklists into Pi-hole gravity.db

set -e

# Update this to your actual GitHub username and repository name
GITHUB_USER="hemiipatu"
REPO_NAME="piholeblocklists"
BRANCH="main"

BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}/blocklists"
GRAVITY_DB="/etc/pihole/gravity.db"

# List of categorized files in your blocklists/ directory
CATEGORIES=(
  "advertisement.txt"
  "fraudulent.txt"
  "malware.txt"
  "phishing.txt"
  "pornography.txt"
  "ransomware.txt"
  "redirect.txt"
  "scam.txt"
)

# Ensure script is running as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run this script with sudo."
  exit 1
fi

# Ensure Pi-hole gravity database exists
if [ ! -f "$GRAVITY_DB" ]; then
  echo "Error: Pi-hole gravity database not found at $GRAVITY_DB."
  exit 1
fi

echo "Adding blocklists to Pi-hole..."

for category in "${CATEGORIES[@]}"; do
  URL="${BASE_URL}/${category}"
  COMMENT="Custom Blocklist: ${category}"
  
  # Insert into Pi-hole adlist table if it doesn't already exist
  sqlite3 "$GRAVITY_DB" "INSERT OR IGNORE INTO adlist (address, comment, enabled) VALUES ('$URL', '$COMMENT', 1);"
  echo "  [+] Added: $category"
done

echo ""
echo "Updating Pi-hole gravity..."
pihole -g

echo ""
echo "Successfully imported all blocklists into Pi-hole!"

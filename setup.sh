#!/usr/bin/env bash

set -e

# Repository configuration
GITHUB_USER="YOUR_USERNAME"
REPO_NAME="YOUR_REPO"
BRANCH="main"

# Path to Pi-hole database
GRAVITY_DB="/etc/pihole/gravity.db"

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[!] Error: This script must be run with sudo."
  exit 1
fi

# Check if Pi-hole gravity database exists
if [ ! -f "$GRAVITY_DB" ]; then
  echo "[!] Error: Pi-hole gravity database not found at $GRAVITY_DB."
  echo "    Please verify Pi-hole is installed correctly."
  exit 1
fi

# Display tier selection menu to user
echo "=================================================================="
echo "          Select Blocklist Protection Tier for Pi-hole            "
echo "=================================================================="
echo " 1) Basic    - Safe protection against malware & phishing."
echo "               (0 false-positive risk)"
echo " 2) Balanced - Recommended for home networks."
echo "               (Includes Ads, Scams, and Trackers)"
echo " 3) Ultimate - Maximum protection."
echo "               (Includes Ransomware, Adult content, & Redirects)"
echo "=================================================================="
read -p "Enter choice [1-3]: " CHOICE

# Assign chosen filename based on selection
case $CHOICE in
  1) FILE="basic.txt" ;;
  2) FILE="balanced.txt" ;;
  3) FILE="ultimate.txt" ;;
  *) echo "[!] Invalid selection. Exiting installation."; exit 1 ;;
esac

# Define raw GitHub URLs
BLOCKLIST_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}/blocklists/${FILE}"
WHITELIST_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}/whitelist.txt"

# Add selected blocklist URL to Pi-hole gravity database
echo ""
echo "[+] Adding ${FILE} blocklist tier to Pi-hole..."
COMMENT="Custom Blocklist Tier (${FILE})"
sqlite3 "$GRAVITY_DB" "INSERT OR IGNORE INTO adlist (address, comment, enabled) VALUES ('$BLOCKLIST_URL', '$COMMENT', 1);"
echo "    Successfully registered blocklist URL."

# Download repository whitelist
echo ""
echo "[+] Fetching repository whitelist from GitHub..."
TEMP_WHITELIST=$(mktemp)

if curl -sSL -f "$WHITELIST_URL" -o "$TEMP_WHITELIST"; then
  DOMAINS_TO_ADD=""
  
  # Clean whitelist entries (remove inline comments and whitespace)
  while IFS= read -r line || [ -n "$line" ]; do
    domain=$(echo "$line" | sed -e 's/#.*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')
    if [ -n "$domain" ]; then
      DOMAINS_TO_ADD="$DOMAINS_TO_ADD $domain"
    fi
  done < "$TEMP_WHITELIST"

  # Apply whitelist domains via Pi-hole CLI
  if [ -n "$DOMAINS_TO_ADD" ]; then
    echo "[+] Applying whitelist entries natively via Pi-hole CLI..."
    pihole -w $DOMAINS_TO_ADD --comment "Auto-added via Repository Setup" > /dev/null
    echo "    Successfully processed whitelisted domains."
  else
    echo "[!] Whitelist file contained no active domain rules. Skipping."
  fi
else
  echo "[!] Warning: Could not download whitelist.txt from repository. Skipping whitelist sync."
fi

# Clean up temporary file
rm -f "$TEMP_WHITELIST"

# Rebuild Pi-hole gravity database
echo ""
echo "[+] Rebuilding Pi-hole Gravity database..."
pihole -g

echo ""
echo "=================================================================="
echo " Setup Complete! Your network is now actively protected by the   "
echo " ${FILE} tier with your whitelist rules applied.                 "
echo "=================================================================="

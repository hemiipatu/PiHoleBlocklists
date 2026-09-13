#!/usr/bin/env bash
set -e

GITHUB_USER="hemiipatu"
REPO_NAME="piholeblocklists"
BRANCH="main"
GRAVITY_DB="/etc/pihole/gravity.db"

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run with sudo."
  exit 1
fi

echo "========================================="
echo " Select Blocklist Protection Level"
echo "========================================="
echo " 1) Basic    - Safe protection against malware & phishing (0 false positives)"
echo " 2) Balanced - Recommended for home networks (Ads, Scams, Trackers)"
echo " 3) Ultimate - Maximum protection (Pornography, Ransomware, Aggressive Tracking)"
echo "========================================="
read -p "Enter choice [1-3]: " CHOICE

case $CHOICE in
  1) FILE="basic.txt" ;;
  2) FILE="balanced.txt" ;;
  3) FILE="ultimate.txt" ;;
  *) echo "Invalid selection. Exiting."; exit 1 ;;
esac

TARGET_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/${BRANCH}/blocklists/${FILE}"

echo "Adding ${FILE} to Pi-hole..."
sqlite3 "$GRAVITY_DB" "INSERT OR IGNORE INTO adlist (address, comment, enabled) VALUES ('$TARGET_URL', 'Custom Blocklist (${FILE})', 1);"

echo "Updating Gravity..."
pihole -g
echo "Done! Running ${FILE} protection tier."

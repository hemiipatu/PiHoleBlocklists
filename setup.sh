#!/usr/bin/env bash
# Installs a versioned Pi-hole blocklist or prints the URL for AdGuard Home.
# Run with Bash and sudo. Pi-hole mode also requires curl, sqlite3, and pihole.

set -euo pipefail

TEMP_BLOCKLIST=""
TEMP_CHECKSUMS=""
TEMP_WHITELIST=""

# Remove temporary downloads on both successful completion and early exit.
cleanup() {
  [ -z "$TEMP_BLOCKLIST" ] || rm -f -- "$TEMP_BLOCKLIST"
  [ -z "$TEMP_CHECKSUMS" ] || rm -f -- "$TEMP_CHECKSUMS"
  [ -z "$TEMP_WHITELIST" ] || rm -f -- "$TEMP_WHITELIST"
}

trap cleanup EXIT

main() {
  GITHUB_USER="hemiipatu"
  REPO_NAME="piholeblocklists"

  GRAVITY_DB="/etc/pihole/gravity.db"

  if [ "$EUID" -ne 0 ]; then
    echo "[!] Error: This script must be run with sudo."
    exit 1
  fi

  echo "=================================================================="
  echo "         Select DNS Blocker Platform for Blocklist Install        "
  echo "=================================================================="
  echo " 1) Pi-hole"
  echo " 2) AdGuard Home"
  echo "=================================================================="
  read -r -p "Enter platform choice [1-2]: " PLATFORM_CHOICE

  case "$PLATFORM_CHOICE" in
    1|2) ;;
    *) echo "[!] Invalid selection. Exiting."; exit 1 ;;
  esac

  echo ""
  echo "=================================================================="
  echo "          Select Blocklist Protection Tier                       "
  echo "=================================================================="
  echo " 1) Basic    - Safe protection against malware & phishing."
  echo " 2) Balanced - Recommended for home networks (Ads, Scams, Trackers)"
  echo " 3) Ultimate - Maximum protection (Porn, Ransomware, Redirects)"
  echo "=================================================================="
  read -r -p "Enter tier choice [1-3]: " TIER_CHOICE

  case $TIER_CHOICE in
    1) FILE="basic.txt" ;;
    2) FILE="balanced.txt" ;;
    3) FILE="ultimate.txt" ;;
    *) echo "[!] Invalid selection. Exiting."; exit 1 ;;
  esac

  # Resolve the moving latest-release alias once, then use its versioned asset URLs.
  RELEASES_API_URL="https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/releases/latest"
  if ! RELEASE_TAG=$(curl -sSLf -H "Accept: application/vnd.github+json" "$RELEASES_API_URL" | sed -n 's/^[[:space:]]*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1); then
    echo "[!] Error: Failed to determine the latest blocklist release."
    exit 1
  fi

  if [[ ! "$RELEASE_TAG" =~ ^v[0-9]+(\.[0-9]+){2}$ ]]; then
    echo "[!] Error: Latest release returned an invalid version tag."
    exit 1
  fi

  RELEASE_BASE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/download/${RELEASE_TAG}"
  BLOCKLIST_URL="${RELEASE_BASE_URL}/${FILE}"
  CHECKSUM_URL="${RELEASE_BASE_URL}/sha256sums.txt"
  WHITELIST_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/main/whitelist.txt"

  # --- SHA256 INTEGRITY VERIFICATION ---
  # This detects mismatches against the release manifest; it is not a signed publisher identity check.
  echo ""
  echo "[+] Fetching blocklist release assets and checksum manifest..."
  TEMP_BLOCKLIST=$(mktemp)
  TEMP_CHECKSUMS=$(mktemp)

  if ! curl -sSLf "$BLOCKLIST_URL" -o "$TEMP_BLOCKLIST"; then
    echo "[!] Error: Failed to download blocklist asset: ${FILE}"
    exit 1
  fi

  if ! curl -sSLf "$CHECKSUM_URL" -o "$TEMP_CHECKSUMS"; then
    echo "[!] Error: Failed to download checksum manifest. Refusing to continue."
    exit 1
  fi

  EXPECTED_HASH=$(awk -v file="$FILE" '$2 == file { print $1 }' "$TEMP_CHECKSUMS")
  if [[ ! "$EXPECTED_HASH" =~ ^[[:xdigit:]]{64}$ ]]; then
    echo "[!] Error: Checksum manifest has no valid SHA256 entry for ${FILE}."
    exit 1
  fi

  echo "[+] Verifying SHA256 checksum for ${FILE}..."
  if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_HASH=$(sha256sum "$TEMP_BLOCKLIST" | awk '{print $1}')
  elif command -v shasum >/dev/null 2>&1; then
    ACTUAL_HASH=$(shasum -a 256 "$TEMP_BLOCKLIST" | awk '{print $1}')
  else
    echo "[!] Error: No SHA256 utility found on system. Refusing to continue."
    exit 1
  fi

  if [ "$EXPECTED_HASH" != "$ACTUAL_HASH" ]; then
    echo "[!] FATAL SECURITY ERROR: Checksum mismatch for ${FILE}!"
    echo "    Expected: ${EXPECTED_HASH}"
    echo "    Got:      ${ACTUAL_HASH}"
    exit 1
  fi
  echo "    ✔ Checksum Verified: Integrity OK (${ACTUAL_HASH:0:12}...)"

  # --- PLATFORM REGISTRATION ---
  if [ "$PLATFORM_CHOICE" -eq 1 ]; then
    # --- PI-HOLE INSTALLATION ---
    if [ ! -f "$GRAVITY_DB" ]; then
      echo "[!] Error: Pi-hole gravity database not found at $GRAVITY_DB."
      exit 1
    fi

    echo ""
    echo "[+] Adding ${FILE} blocklist tier to Pi-hole..."
    COMMENT="Custom Blocklist Tier (${FILE})"
    # Avoid adding duplicate entries when setup is run more than once.
    sqlite3 "$GRAVITY_DB" "INSERT OR IGNORE INTO adlist (address, comment, enabled) VALUES ('$BLOCKLIST_URL', '$COMMENT', 1);"

    echo "[+] Fetching repository whitelist from GitHub..."
    TEMP_WHITELIST=$(mktemp)
    if curl -sSL -f "$WHITELIST_URL" -o "$TEMP_WHITELIST"; then
      DOMAINS_TO_ADD=""
      while IFS= read -r line || [ -n "$line" ]; do
        domain=$(echo "$line" | sed -e 's/#.*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')
        if [ -n "$domain" ]; then
          DOMAINS_TO_ADD="$DOMAINS_TO_ADD $domain"
        fi
      done < "$TEMP_WHITELIST"

      if [ -n "$DOMAINS_TO_ADD" ]; then
        echo "[+] Applying whitelist entries via Pi-hole CLI..."
        echo "$DOMAINS_TO_ADD" | xargs -n 50 pihole -w --comment "Auto-added via Repository Setup" > /dev/null
      fi
    fi
    echo "[+] Rebuilding Pi-hole Gravity database..."
    pihole -g

  elif [ "$PLATFORM_CHOICE" -eq 2 ]; then
    # --- ADGUARD HOME INSTALLATION ---
    # AdGuard Home is configured manually; this mode only prints the verified release URL.
    echo ""
    echo "[+] Verified Release Blocklist URL for AdGuard Home:"
    echo "    Blocklist URL: $BLOCKLIST_URL"
    echo ""
    echo "To add this in AdGuard Home:"
    echo " 1. Open AdGuard Home Web UI"
    echo " 2. Go to Filters -> DNS blocklists -> Add blocklist -> Add a custom list"
    echo " 3. Name: PiHoleBlocklists (${FILE})"
    echo " 4. URL: $BLOCKLIST_URL"
  else
    echo "[!] Invalid platform choice. Exiting."
    exit 1
  fi

  echo ""
  echo "=================================================================="
  echo " Setup Complete! Network protection successfully updated.         "
  echo "=================================================================="
}

main "$@"

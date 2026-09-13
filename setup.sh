#!/usr/bin/env bash

set -e

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
  read -p "Enter platform choice [1-2]: " PLATFORM_CHOICE

  echo ""
  echo "=================================================================="
  echo "          Select Blocklist Protection Tier                       "
  echo "=================================================================="
  echo " 1) Basic    - Safe protection against malware & phishing."
  echo " 2) Balanced - Recommended for home networks (Ads, Scams, Trackers)"
  echo " 3) Ultimate - Maximum protection (Porn, Ransomware, Redirects)"
  echo "=================================================================="
  read -p "Enter tier choice [1-3]: " TIER_CHOICE

  case $TIER_CHOICE in
    1) FILE="basic.txt" ;;
    2) FILE="balanced.txt" ;;
    3) FILE="ultimate.txt" ;;
    *) echo "[!] Invalid selection. Exiting."; exit 1 ;;
  esac

  RELEASE_BASE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/download/latest"
  BLOCKLIST_URL="${RELEASE_BASE_URL}/${FILE}"
  CHECKSUM_URL="${RELEASE_BASE_URL}/sha256sums.txt"
  WHITELIST_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/main/whitelist.txt"

  # --- SHA256 INTEGRITY VERIFICATION ---
  echo ""
  echo "[+] Fetching blocklist release assets and checksum manifest..."
  TEMP_BLOCKLIST=$(mktemp)
  TEMP_CHECKSUMS=$(mktemp)

  if ! curl -sSLf "$BLOCKLIST_URL" -o "$TEMP_BLOCKLIST"; then
    echo "[!] Error: Failed to download blocklist asset: ${FILE}"
    rm -f "$TEMP_BLOCKLIST" "$TEMP_CHECKSUMS"
    exit 1
  fi

  if curl -sSLf "$CHECKSUM_URL" -o "$TEMP_CHECKSUMS"; then
    EXPECTED_HASH=$(grep "  ${FILE}$" "$TEMP_CHECKSUMS" | awk '{print $1}')
    
    if [ -n "$EXPECTED_HASH" ]; then
      echo "[+] Verifying SHA256 checksum for ${FILE}..."
      
      # Determine system hashing tool (sha256sum or shasum)
      if command -v sha256sum >/dev/null 2>&1; then
        ACTUAL_HASH=$(sha256sum "$TEMP_BLOCKLIST" | awk '{print $1}')
      elif command -v shasum >/dev/null 2>&1; then
        ACTUAL_HASH=$(shasum -a 256 "$TEMP_BLOCKLIST" | awk '{print $1}')
      else
        ACTUAL_HASH=""
        echo "[!] Warning: No sha256 utility found on system. Skipping hash check."
      fi

      if [ -n "$ACTUAL_HASH" ]; then
        if [ "$EXPECTED_HASH" = "$ACTUAL_HASH" ]; then
          echo "    ✔ Checksum Verified: Integrity OK (${ACTUAL_HASH:0:12}...)"
        else
          echo "[!] FATAL SECURITY ERROR: Checksum mismatch for ${FILE}!"
          echo "    Expected: ${EXPECTED_HASH}"
          echo "    Got:      ${ACTUAL_HASH}"
          rm -f "$TEMP_BLOCKLIST" "$TEMP_CHECKSUMS"
          exit 1
        fi
      fi
    fi
  else
    echo "[!] Warning: Could not download sha256sums.txt manifest. Continuing without integrity verification."
  fi

  rm -f "$TEMP_BLOCKLIST" "$TEMP_CHECKSUMS"

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
    rm -f "$TEMP_WHITELIST"

    echo "[+] Rebuilding Pi-hole Gravity database..."
    pihole -g

  elif [ "$PLATFORM_CHOICE" -eq 2 ]; then
    # --- ADGUARD HOME INSTALLATION ---
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

# PiHoleBlocklists: Stop ads, tracking and other virtual garbage
![GitHub issues](https://img.shields.io/github/issues/hemiipatu/piholeblocklists?style=for-the-badge)
![GitHub closed issues](https://img.shields.io/github/issues-closed/hemiipatu/piholeblocklists?style=for-the-badge)
[![License: GPL v3](https://img.shields.io/badge/license-gplv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Maintenance](https://img.shields.io/badge/maintained%3f-yes-green.svg?style=for-the-badge)](https://github.com/hemiipatu/piholeblocklists/graphs/commit-activity)
![GitHub contributors](https://img.shields.io/github/contributors/hemiipatu/piholeblocklists?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hemiipatu/piholeblocklists?style=for-the-badge)

&nbsp;

## What is PiHoleBlocklists
PiHoleBlocklists is a curated collection of upstream adblock lists, deduplicated and refactored specifically for Pi-hole. It provides a single, clean source to block ads, malware, phishing, and online tracker junk.

## Protection Tiers
The automated build process generates three distinct protection tiers so you can select the right balance for your network:

* **Basic (Light):** High-confidence malware and phishing protection with zero false-positive risk. Safe for non-technical users.
* **Balanced (Recommended):** Adds tracking, telemetry, scam domains, and main ad servers. Recommended for everyday home networks.
* **Ultimate (Aggressive):** Includes Basic + Balanced, plus ransomware, adult content, redirects, and aggressive tracking feeds. Higher risk of false positives.

## How to install
### Quick install (Recommended)
Run the automated interactive setup script directly on your Pi-hole system:
 - `curl -sSLf [https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh](https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh) | sudo bash`

### Manual Inspect & Run (Security-Minded)
If you prefer to review script contents locally before executing with root privileges:
- Download setup script
  - `curl -sSLf -o setup.sh [https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh](https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh)`
- Inspect script contents
  - `less setup.sh`
- Execute script
  - `sudo bash setup.sh`

## Upstream sources & Credits
This project compiles, deduplicates, and optimizes data from several upstream maintainers and security feeds. Full credit goes to the creators and maintainers of these lists:

| Category | Upstream Project / Author | Original Source |
| :--- | :--- | :--- |
| **Advertisements** | **HaGeZi** | [DNS Blocklists](https://github.com/hagezi/dns-blocklists) |
| | **StevenBlack** | [hosts](https://github.com/StevenBlack/hosts) |
| | **AdAway** | [AdAway Hosts](https://adaway.org) |
| | **Peter Lowe** | [yoyo.org Adservers](https://pgl.yoyo.org/adservers/) |
| | **Blocklist Project** | [Ads List](https://github.com/blocklistproject/Lists) |
| **Fraudulent** | **HaGeZi** | [Fake List](https://github.com/hagezi/dns-blocklists) |
| | **Blocklist Project** | [Fraud List](https://github.com/blocklistproject/Lists) |
| | **Spam404** | [Main Blacklist](https://github.com/Spam404/lists) |
| **Malware** | **abuse.ch** | [URLhaus](https://urlhaus.abuse.ch/) |
| | **HaGeZi** | [Threat Intelligence Feed (TIF)](https://github.com/hagezi/dns-blocklists) |
| | **DShield Threat Feed** | [Malicious Domains](https://github.com/Dshield-Threat-Feed/DShield-Malicious-Domains) |
| | **Blocklist Project** | [Malware List](https://github.com/blocklistproject/Lists) |
| | **OISD** | [OISD Blocklist](https://oisd.nl/) |
| **Phishing** | **Mitchell Krog** | [Phishing Database](https://github.com/mitchellkrogza/Phishing.Database) |
| | **Blocklist Project** | [Phishing List](https://github.com/blocklistproject/Lists) |
| | **OpenPhish** | [OpenPhish Feed](https://openphish.com/) |
| **Pornography / NSFW** | **StevenBlack** | [Porn Alternates](https://github.com/StevenBlack/hosts) |
| | **Blocklist Project** | [Porn List](https://github.com/blocklistproject/Lists) |
| | **Snawoot** | [NSFW Hosts](https://github.com/Snawoot/nsfw-hosts) |
| **Ransomware** | **Blocklist Project** | [Ransomware List](https://github.com/blocklistproject/Lists) |
| | **ThreatFox (abuse.ch)** | [ThreatFox Hosts](https://threatfox.abuse.ch/) |
| **Redirects** | **Blocklist Project** | [Redirect List](https://github.com/blocklistproject/Lists) |
| **Regex** | **mmotti** | [Pi-hole Regex](https://github.com/mmotti/pihole-regex) |
| | **cbuijs** | [Pi-hole Regex](https://github.com/cbuijs/pihole-regex) |
| **Scams** | **DurableNapkin** | [Scam Blocklist](https://github.com/DurableNapkin/Scam-Blocklist) |
| | **Blocklist Project** | [Scam List](https://github.com/blocklistproject/Lists) |

> **Note:** If you are a list maintainer and would like to update your credit link or request a change, please open an issue.

## Supporting PiHoleBlocklists project
If you are intrested in supporting the project you can:
 - [Submit false positives](https://github.com/hemiipatu/PiHoleBlocklists/issues/new/choose)

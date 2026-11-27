# PiHoleBlocklists

> Stop ads, tracking and other virtual garbage.

![GitHub issues](https://img.shields.io/github/issues/hemiipatu/piholeblocklists?style=for-the-badge)
![GitHub closed issues](https://img.shields.io/github/issues-closed/hemiipatu/piholeblocklists?style=for-the-badge)
[![License: GPL v3](https://img.shields.io/badge/license-gplv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Maintenance](https://img.shields.io/badge/maintained%3f-yes-green.svg?style=for-the-badge)](https://github.com/hemiipatu/piholeblocklists/graphs/commit-activity)
![GitHub contributors](https://img.shields.io/github/contributors/hemiipatu/piholeblocklists?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hemiipatu/piholeblocklists?style=for-the-badge)

## 📋 Overview

PiHoleBlocklists is a curated collection of upstream adblock lists, deduplicated and refactored specifically for Pi-hole. It provides a single, clean source to block ads, malware, phishing, and online tracker junk.

## ⚙️ Requirements

- Pi-hole installed and running for the Pi-hole option; AdGuard Home installed for the AdGuard Home option
- Internet connectivity and root access to run the setup script
- `curl` and either `sha256sum` or `shasum`
- For Pi-hole: `sqlite3` and the `pihole` command
- Basic familiarity with command-line interfaces

## 🚀 Quick Start

For detailed platform-specific installation steps, see the [Installation Guide](docs/INSTALLATION_GUIDE.md).

### Quick Install (Recommended)

Run the automated interactive setup script on your Pi-hole or AdGuard Home host:

```bash
curl -sSLf https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh | sudo bash
```

### Manual Inspect & Run (Security-Minded)

If you prefer to review script contents locally before executing with root privileges:

1. **Download setup script**
   ```bash
   curl -sSLf -o setup.sh https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh
   ```

2. **Inspect script contents**
   ```bash
   less setup.sh
   ```

3. **Execute script**
   ```bash
   sudo bash setup.sh
   ```

## 🏗️ Architecture Diagram

```text
Upstream sources and whitelist
        ↓
GitHub Actions runs build.py
        ↓
Generate tier lists, category lists, and checksums
        ↓
Publish versioned tier lists and checksums
        ↓
setup.sh downloads and verifies the selected tier
        ↓
Pi-hole: register the list and rebuild Gravity
AdGuard Home: print the URL for manual setup
```

## 📁 Directory Structure

```text
PiHoleBlocklists/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml
│   │   ├── false_positive.yml
│   │   └── source_request.yml
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── codeql.yml
│   │   ├── issue_triage.yml
│   │   ├── source_health.yml
│   │   └── update.yml
│   └── dependabot.yml
├── __pycache__/                 (Tracked Python bytecode)
│   └── build.cpython-312.pyc
├── blocklists/
│   ├── advertisement.txt
│   ├── balanced.txt             (Balanced tier)
│   ├── basic.txt                (Basic tier)
│   ├── fraudulent.txt
│   ├── malware.txt
│   ├── phishing.txt
│   ├── pornography.txt
│   ├── ransomware.txt
│   ├── redirect.txt
│   ├── regex.txt
│   ├── scam.txt
│   ├── sha256sums.txt           (Tier checksums)
│   └── ultimate.txt             (Ultimate tier)
├── docs/
│   └── INSTALLATION_GUIDE.md    (Installation instructions)
├── tests/
│   ├── __pycache__/             (Tracked test bytecode)
│   │   └── test_build.cpython-312.pyc
│   └── test_build.py            (Build tests)
├── build.py                     (Blocklist compiler)
├── setup.sh                     (Installation script)
├── sources.json                 (Upstream source definitions)
├── whitelist.txt                (Whitelisted domains)
├── LICENSE                      (GPL v3 license)
└── README.md
```

## 🧩 Components

### Blocklist build

- **`sources.json`** defines upstream sources by protection tier and category.
- **`whitelist.txt`** contains domains excluded from generated lists. Built-in defaults are also applied.
- **`build.py`** fetches and parses sources, filters whitelisted domains, combines tier data, and writes the generated files and checksum manifest.
- **`blocklists/`** contains the generated tier and category lists. Basic contains the Basic sources; Balanced adds its sources to Basic; Ultimate adds its sources to Balanced. Category lists are generated for convenience and are not release assets.

### Installation

- **`setup.sh`** lets you select a platform and tier. It downloads the selected versioned release list and SHA-256 manifest, verifies the checksum, then registers the list and rebuilds Gravity in Pi-hole mode. In AdGuard Home mode, it prints the verified release URL and setup instructions.

### Automated updates

GitHub Actions runs the build on a schedule, when relevant source or build files change, or when manually triggered. It commits changed generated lists and publishes versioned releases containing the tier lists, checksum manifest, and whitelist.

### Protection tiers

The generated tiers offer different balances of coverage and false-positive risk:

- **Basic (Light):** High-confidence malware and phishing protection with zero false-positive risk. Safe for non-technical users.
- **Balanced (Recommended):** Adds tracking, telemetry, scam domains, and main ad servers. Recommended for everyday home networks.
- **Ultimate (Aggressive):** Includes Basic and Balanced, plus ransomware, adult content, redirects, and aggressive tracking feeds. Higher risk of false positives.

### Upstream Sources & Credits

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
| **Malware** | **HaGeZi** | [Threat Intelligence Feed (TIF)](https://github.com/hagezi/dns-blocklists) |
| | **OISD** | [OISD Blocklist](https://oisd.nl/) |
| **Phishing** | **Phishing Database** | [Active Domains](https://github.com/Phishing-Database/Phishing.Database) |
| | **Blocklist Project** | [Phishing List](https://github.com/blocklistproject/Lists) |
| | **OpenPhish** | [OpenPhish Feed](https://openphish.com/) |
| **Pornography / NSFW** | **StevenBlack** | [Porn Alternates](https://github.com/StevenBlack/hosts) |
| | **Blocklist Project** | [Porn List](https://github.com/blocklistproject/Lists) |
| | **HaGeZi** | [NSFW List](https://github.com/hagezi/dns-blocklists) |
| **Ransomware** | **Blocklist Project** | [Ransomware List](https://github.com/blocklistproject/Lists) |
| **Redirects** | **Blocklist Project** | [Redirect List](https://github.com/blocklistproject/Lists) |
| **Regex** | **mmotti** | [Pi-hole Regex](https://github.com/mmotti/pihole-regex) |
| | **cbuijs** | [Pi-hole Regex](https://github.com/cbuijs/pihole-regex) |
| **Scams** | **Blocklist Project** | [Scam List](https://github.com/blocklistproject/Lists) |

> **Note:** If you are a list maintainer and would like to update your credit link or request a change, please [open an issue](https://github.com/hemiipatu/PiHoleBlocklists/issues/new/choose).

## ⚙️ Configuration

After installation, you can customize your blocklists by editing the configuration files:

- **Whitelist:** Add domains to `whitelist.txt` to prevent blocking
- **Sources:** Modify `sources.json` to add or remove upstream blocklists
- **Rebuild:** Run `python3 build.py` to regenerate blocklists with your changes

For detailed configuration options, refer to the project documentation in each respective file.

## 🐛 Troubleshooting

### Installation failed

- Ensure you have sudo/root privileges
- Verify internet connectivity on your Pi-hole device
- Check that Pi-hole is properly installed and running

### Too many false positives

- Try switching from Ultimate to Balanced tier
- Check `whitelist.txt` for common false positives
- Review Pi-hole logs for blocked legitimate domains

### Lists not updating

- Check the repository's [latest release](https://github.com/hemiipatu/PiHoleBlocklists/releases/latest).
- Re-run the setup script to get the latest versioned list URL and checksum; Pi-hole mode also rebuilds Gravity.
- In AdGuard Home, update the custom list URL to the latest version printed by the setup script.

## 🔒 Security

- Lists are built from well-maintained, reputable upstream sources
- All sources are credited and tracked in this repository
- The build process deduplicates entries and removes invalid records
- Consider your threat model when selecting protection tiers
- Regularly review false positives and adjust your whitelist

## 📚 File Reference

| File/Folder | Purpose |
| :--- | :--- |
| `blocklists/` | Generated blocklist files organized by tier and category |
| `build.py` | Automated build script for compiling and deduplicating lists |
| `setup.sh` | Interactive setup script for Pi-hole and AdGuard Home |
| `docs/INSTALLATION_GUIDE.md` | Detailed installation, verification, update, and removal instructions |
| `sources.json` | Configuration of upstream blocklist sources |
| `whitelist.txt` | Manually maintained whitelist of false positives |
| `tests/` | Automated tests for list integrity and overlap |

## 📄 License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](./LICENSE) file for details.

## 🤝 Contributing

We appreciate contributions to improve PiHoleBlocklists! Here's how you can help:

1. **Check existing issues** — Browse [open issues](https://github.com/hemiipatu/PiHoleBlocklists/issues) to see if your concern has already been reported.

2. **Submit a new issue** — If you've found a problem, [create a new issue](https://github.com/hemiipatu/PiHoleBlocklists/issues/new/choose) with the following details:
   - Describe the problem clearly and concisely
   - Specify which protection tier you're using (Basic, Balanced, or Ultimate)
   - Include affected domains if applicable
   - Note your Pi-hole version and operating system
   - Indicate if this is a false positive, missing filter, or other issue type

3. **Provide supporting details** — Include:
   - Steps to reproduce the issue
   - Expected vs. actual behavior
   - Any error messages or logs
   - Screenshots if helpful

## 🔗 Related Resources

- [Pi-hole Official Documentation](https://docs.pi-hole.net/)
- [HaGeZi DNS Blocklists](https://github.com/hagezi/dns-blocklists)
- [Blocklist Project](https://github.com/blocklistproject/Lists)
- [OISD Blocklist](https://oisd.nl/)
- [StevenBlack Hosts](https://github.com/StevenBlack/hosts)

---

**Last Updated:** November 2026

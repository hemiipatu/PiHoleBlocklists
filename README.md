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

## ✅ Requirements

- Pi-hole installed and running on your system
- Internet connectivity on your Pi-hole device
- Sudo/root access for installation
- Basic familiarity with command-line interfaces

## 🚀 Quick Start

### Quick Install (Recommended)

Run the automated interactive setup script directly on your Pi-hole system:

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

## 🛡️ Protection Tiers

The automated build process generates three distinct protection tiers so you can select the right balance for your network:

- **Basic (Light):** High-confidence malware and phishing protection with zero false-positive risk. Safe for non-technical users.
- **Balanced (Recommended):** Adds tracking, telemetry, scam domains, and main ad servers. Recommended for everyday home networks.
- **Ultimate (Aggressive):** Includes Basic + Balanced, plus ransomware, adult content, redirects, and aggressive tracking feeds. Higher risk of false positives.

## 📚 Directory Structure

```
PiHoleBlocklists/
├── blocklists/          # Generated blocklist files
├── tests/               # Test suite
├── build.py             # Build automation script
├── setup.sh             # Installation script
├── sources.json         # Upstream source definitions
├── whitelist.txt        # Whitelisted domains
└── README.md            # This file
```

## 📄 File Reference

| File/Folder | Purpose |
| :--- | :--- |
| `blocklists/` | Generated blocklist files organized by tier and category |
| `build.py` | Automated build script for compiling and deduplicating lists |
| `setup.sh` | Interactive installation script for Pi-hole |
| `sources.json` | Configuration of upstream blocklist sources |
| `whitelist.txt` | Manually maintained whitelist of false positives |
| `tests/` | Automated tests for list integrity and overlap |

## 🔗 Upstream Sources & Credits

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

## 🔧 Troubleshooting

### Installation failed
- Ensure you have sudo/root privileges
- Verify internet connectivity on your Pi-hole device
- Check that Pi-hole is properly installed and running

### Too many false positives
- Try switching from Ultimate to Balanced tier
- Check `whitelist.txt` for common false positives
- Review Pi-hole logs for blocked legitimate domains

### Lists not updating
- Verify cron job is installed: `crontab -l`
- Check logs in `/var/log/pihole.log`
- Re-run setup script to restore automatic updates

## 🔒 Security

- Lists are built from well-maintained, reputable upstream sources
- All sources are credited and tracked in this repository
- The build process deduplicates entries and removes invalid records
- Consider your threat model when selecting protection tiers
- Regularly review false positives and adjust your whitelist

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

## 📖 Related Resources

- [Pi-hole Official Documentation](https://docs.pi-hole.net/)
- [HaGeZi DNS Blocklists](https://github.com/hagezi/dns-blocklists)
- [Blocklist Project](https://github.com/blocklistproject/Lists)
- [OISD Blocklist](https://oisd.nl/)
- [StevenBlack Hosts](https://github.com/StevenBlack/hosts)

---

**Last Updated:** November 2026

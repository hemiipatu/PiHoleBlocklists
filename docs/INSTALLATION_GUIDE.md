# PiHoleBlocklists Installation Guide

> A step-by-step guide to install, verify, update, and remove PiHoleBlocklists with Pi-hole or AdGuard Home.

## 📋 Overview

This guide covers installing PiHoleBlocklists with Pi-hole or AdGuard Home. For the project overview, architecture, and generated blocklist details, see the [README.md](../README.md).

## ⚙️ Requirements

### Prerequisites Checklist

- [ ] A Pi-hole or AdGuard Home installation, depending on the platform you want to configure
- [ ] Internet access from the device running the setup script
- [ ] `curl` and either `sha256sum` or `shasum`
- [ ] Root privileges to run the setup script (`sudo` on Linux)
- [ ] For Pi-hole: Pi-hole installed, the `pihole` command and `sqlite3` available, and `/etc/pihole/gravity.db` present
- [ ] For AdGuard Home: access to its web interface to add the printed blocklist URL

The script requires root privileges for both platform choices. The AdGuard Home option verifies and prints a URL; it does not change AdGuard Home configuration automatically.

## 🚀 Quick Start

### Quick Install (Recommended)

Run this on the Pi-hole or AdGuard Home host:

```bash
curl -sSLf https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh | sudo bash
```

The script prompts you to select:

1. **Platform:** Pi-hole or AdGuard Home
2. **Tier:** Basic, Balanced, or Ultimate

Follow the displayed instructions to finish the selected platform's setup. For AdGuard Home, you must add the printed URL in its web interface.

### Manual Inspect & Run (Security-Minded)

If you prefer to inspect the script before running it with root privileges:

1. **Download the setup script**
   ```bash
   curl -sSLf -o setup.sh https://raw.githubusercontent.com/hemiipatu/piholeblocklists/main/setup.sh
   ```

2. **Inspect the script**
   Open `setup.sh` in a text editor or inspect it in the terminal:
   ```bash
   less setup.sh
   ```

3. **Run the script**
   ```bash
   sudo bash setup.sh
   ```

Choose a platform and tier when prompted. The script reports errors if it cannot resolve a supported release tag, download the selected list or checksum manifest, or verify the checksum.

## 🧩 Components

### Setup Script

The setup script retrieves the latest versioned GitHub release, downloads the selected tier and its SHA-256 manifest, and verifies that the file matches the manifest before proceeding.

- **Pi-hole:** Adds the selected versioned list URL to Pi-hole, attempts to apply domains from the repository whitelist, and runs `pihole -g` to rebuild Gravity.
- **AdGuard Home:** Prints the verified versioned list URL and instructions for adding it through the AdGuard Home web interface.

### Protection Tiers

| Tier | Coverage | Considerations |
| :--- | :--- | :--- |
| **Basic** | Malware, phishing, and a small set of ad sources | Lightest option |
| **Balanced** | Basic plus broader ad, fraud, and scam sources | Recommended for many home networks |
| **Ultimate** | Balanced plus additional malware, adult-content, ransomware, and redirect sources | Broadest coverage; greater false-positive risk |

## ✅ Verification Steps

### Pi-hole

1. Confirm the setup script completed its Gravity rebuild without errors.
2. In the Pi-hole admin interface, open the Adlists management page and confirm the PiHoleBlocklists release URL is present and enabled.
3. To inspect the configured entries from a terminal:

   ```bash
   sudo sqlite3 /etc/pihole/gravity.db \
     "SELECT address, enabled, comment FROM adlist WHERE comment LIKE 'Custom Blocklist Tier%';"
   ```

4. Confirm clients are using Pi-hole for DNS and review Pi-hole's query log when checking whether a domain is blocked.

### AdGuard Home

1. In the AdGuard Home web interface, add the verified URL printed by the setup script as a custom DNS blocklist.
2. Confirm the list is enabled and its update status is successful.
3. Check AdGuard Home's query log to confirm client DNS requests are reaching the server.

---

## ⚙️ Configuration

Choose a tier during setup to control the balance between coverage and false-positive risk. The source definitions and whitelist used to build published lists are maintained in the repository; editing local copies does not change the already published release lists.

For details about the tiers, source data, and generated files, see the [README.md](../README.md).

### Updating or Changing Tiers

The installer uses versioned release URLs. Running it again resolves the current release and prompts you to select a platform and tier.

#### Pi-hole

1. Run the setup command again and choose the desired tier.
2. The new release URL is added to Pi-hole; the previous versioned entry is not automatically removed.
3. In the Pi-hole Adlists management page, remove older PiHoleBlocklists entries or tiers you no longer want.
4. Rebuild Gravity after removing entries:

   ```bash
   sudo pihole -g
   ```

#### AdGuard Home

Run the setup script again, then replace the existing custom-list URL in AdGuard Home with the new versioned URL it prints. The script does not update the AdGuard Home configuration itself.

## 🐛 Troubleshooting

### "This script must be run with sudo"

Run the script with root privileges:

```bash
sudo bash setup.sh
```

The script checks for root privileges even when selecting the AdGuard Home option.

### Pi-hole gravity database not found

Run the script on the Pi-hole host and confirm Pi-hole is installed and `/etc/pihole/gravity.db` exists. The AdGuard Home option does not require this database, but the script still requires root privileges.

### A required command is missing

Confirm `curl` and a SHA-256 utility (`sha256sum` or `shasum`) are available. Pi-hole mode also requires `sqlite3` and the `pihole` command.

### Latest release cannot be found or has an invalid tag

Check internet access to GitHub and confirm the project has a versioned release. The installer expects a version tag in the `vX.Y.Z` format.

### Checksum verification fails

Do not continue with a file that fails verification. Retry later and check the project's [releases](https://github.com/hemiipatu/PiHoleBlocklists/releases) for a valid tier file and checksum manifest.

### AdGuard Home is not using the selected list

The script only prints a URL for AdGuard Home. Add that URL as a custom DNS blocklist in its web interface, enable the list, and refresh its status.

### A domain is still accessible or a site is not working

- Confirm the intended tier is enabled and the DNS service has refreshed its lists.
- Confirm affected clients use the Pi-hole or AdGuard Home server.
- Review the query log and consider whether a different tier or an allowlist exception is appropriate.

## 🗑️ Uninstallation

### Pi-hole

1. Open the Pi-hole Adlists management page.
2. Remove only the PiHoleBlocklists versioned URL entries you want to uninstall; leave other lists intact.
3. Rebuild Gravity:

   ```bash
   sudo pihole -g
   ```

The setup script may also add repository whitelist domains with the comment `Auto-added via Repository Setup`. Removing the blocklist does not remove these allowlist entries. Review them separately and remove only entries you have confirmed are no longer needed.

### AdGuard Home

Remove the PiHoleBlocklists custom DNS blocklist from the AdGuard Home web interface.

## 🔒 Security

- The quick-install command runs a remotely downloaded script with root privileges. Review the script first if you want to inspect it before execution.
- The installer checks the downloaded blocklist against a SHA-256 manifest. This detects a mismatch but does not prove the manifest's publisher identity; the manifest is not signed.
- Pi-hole mode writes a list entry to the Pi-hole database, may add whitelist entries, and rebuilds Gravity.
- Review the protection tiers and monitor for false positives after installation.

## 📝 File Reference

| File/Folder | Purpose |
| :--- | :--- |
| `.github/` | Issue templates and automated workflows |
| `blocklists/` | Generated tier and category lists |
| `build.py` | Compiles upstream sources into blocklists |
| `setup.sh` | Interactive installer for Pi-hole and AdGuard Home |
| `sources.json` | Upstream source definitions used to build published lists |
| `whitelist.txt` | Repository allowlist applied by the Pi-hole setup option |
| `tests/` | Automated tests for the build process |
| `README.md` | Project overview, architecture, and configuration details |
| `docs/INSTALLATION_GUIDE.md` | This installation and maintenance guide |
| `LICENSE` | GNU General Public License v3.0 |

## 📄 License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

To report a problem or suggest an improvement, follow the [contribution steps in the README](../README.md#contributing).

## 🔗 Related Resources

If you need help:

1. Review the [README.md](../README.md) for project details and tier descriptions.
2. Check [existing issues](https://github.com/hemiipatu/PiHoleBlocklists/issues).
3. [Open a new issue](https://github.com/hemiipatu/PiHoleBlocklists/issues/new/choose) and include your platform, selected tier, affected domains, relevant error output, and steps to reproduce.

- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [AdGuard Home Documentation](https://github.com/AdguardTeam/AdGuardHome/wiki)
- [Project Releases](https://github.com/hemiipatu/PiHoleBlocklists/releases)

---

**Last Updated:** November 2026

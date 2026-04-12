# FritzBox Restart

A simple, safe automation tool to reboot your AVM FRITZ!Box router -- with two methods to choose from:

- **API (TR-064)** -- Lightweight SOAP call, no browser needed
- **Web (Playwright)** -- Browser automation through the FritzBox web interface

> Tested with **FritzBox 7590** running **FritzOS 8.21**

---

## Features

- **Two reboot methods** -- Choose between the fast TR-064 API or the proven Playwright web automation
- Built-in safety confirmation before execution
- Credentials stored securely in a local `.env` file (excluded from git)
- Clean, readable CLI output with step-by-step progress
- Main script with method selection or standalone scripts for each method

## Prerequisites

- Python 3.8+
- A FRITZ!Box router accessible on your local network

### For the API method (TR-064)

In your FritzBox web interface, enable TR-064 access:

**Heimnetz > Netzwerk > Netzwerkeinstellungen > "Zugriff fuer Anwendungen zulassen"**
*(Home Network > Network > Network Settings > "Allow access for applications")*

### For the Web method (Playwright)

Chromium must be installed via Playwright:

```bash
playwright install chromium
```

## Installation

```bash
# Clone the repository
git clone https://github.com/arithmetic-zz/FritzBox-Restart.git
cd FritzBox-Restart

# Install dependencies
pip install -r requirements.txt

# Only needed for the Web/Playwright method:
playwright install chromium
```

## Configuration

Create a `.env` file in the project root with your FritzBox credentials:

```env
FRITZBOX_URL=http://fritz.box
FRITZBOX_USERNAME=
FRITZBOX_PASSWORD=your_password_here
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `FRITZBOX_PASSWORD` | Yes | -- | Your FritzBox login password |
| `FRITZBOX_URL` | No | `http://fritz.box` | URL or IP of your FritzBox |
| `FRITZBOX_USERNAME` | No | *(empty)* | Username (only needed if multiple users are configured on the FritzBox) |

> **Note:** The `.env` file is excluded from version control via `.gitignore`. Never commit your credentials.

## Usage

### Main script (interactive method selection)

```bash
python3 fritzbox_reboot.py
```

### Main script with CLI argument

```bash
python3 fritzbox_reboot.py --method api   # Use TR-064 API
python3 fritzbox_reboot.py --method web   # Use Playwright
```

### Standalone scripts

```bash
python3 fritzbox_reboot_api.py   # TR-064 API directly
python3 fritzbox_reboot_web.py   # Playwright directly
```

### Example Output (API)

```
====================================================
  FritzBox Restart (API/TR-064) - Version 2.0
  Tested with FritzOS: 8.21
====================================================

  Are you sure you want to reboot your FritzBox? (yes/no): y

  -> Connecting to fritz.box via TR-064 ...
  -> Connected to FRITZ!Box 7590 (FritzOS 8.21).
  -> Sending reboot command ...

  [OK] FritzBox reboot triggered successfully.
  The router will restart now. This takes about 1-2 minutes.

  Save reboot command as standalone curl script? (yes/no): y

  [OK] Curl script saved to: /path/to/reboot_fritzbox.sh
  Run it with: ./reboot_fritzbox.sh
```

### Standalone curl script

After a successful API reboot, you can save the reboot command as a standalone shell script (`reboot_fritzbox.sh`). This script uses plain `curl` with TR-064 SOAP — no Python required. Your credentials are embedded inline, so you can copy it anywhere and run it directly.

> **Note:** The generated script contains your password in plain text and is excluded from version control via `.gitignore`.

```bash
./reboot_fritzbox.sh
```

### Example Output (Web)

```
====================================================
  FritzBox Restart (Web/Playwright) - Version 2.0
  Tested with FritzOS: 8.21
====================================================

  Are you sure you want to reboot your FritzBox? (yes/no): y

  -> Connecting to http://fritz.box ...
  -> Logging in ...
  -> Login successful.
  -> Navigating to System > Sicherung (Backup) ...
  -> Looking for 'FRITZ!Box neu starten' card ...
  -> Clicking 'FRITZ!Box neu starten' ...
  -> Looking for confirmation button 'Neu starten' ...
  -> Confirming with 'Neu starten' ...

  [OK] FritzBox reboot triggered successfully.
  The router will restart now. This takes about 1-2 minutes.
```

## Safety

### API method

The TR-064 API sends a single `Reboot` SOAP command. No other actions are possible through this code path.

### Web method

The Playwright script is designed with multiple layers of protection:

1. **User confirmation** -- You must type `yes` or `y` before anything happens
2. **Exact text matching** -- The script verifies the exact text content of every element before clicking
3. **Abort on mismatch** -- If any element text doesn't match expectations, the script aborts immediately
4. **No destructive actions** -- Factory reset, backup overwrite, and restore buttons are never interacted with

## How It Works

### API method (TR-064)

Uses the [fritzconnection](https://github.com/kbr/fritzconnection) library to call the `DeviceConfig1:Reboot` action via the FritzBox's TR-064 SOAP interface. Authentication uses HTTP Digest. This is the fastest and most reliable method.

### Web method (Playwright)

Uses Playwright to automate a Chromium browser:

1. Opens the FritzBox web interface
2. Logs in with the credentials from `.env`
3. Navigates to **System > Sicherung** (System > Backup)
4. Clicks the **"FRITZ!Box neu starten"** (restart FRITZ!Box) card (with text verification)
5. Confirms the reboot by clicking **"Neu starten"** (restart) (with text verification)
6. Closes the browser

## Compatibility

| FritzBox Model | FritzOS Version | Status |
|---|---|---|
| 7590 | 8.21 | Tested |

> Other FritzBox models with FritzOS 7.x+ may work but are untested. Contributions welcome!

## License

This project is licensed under the [MIT License](LICENSE).

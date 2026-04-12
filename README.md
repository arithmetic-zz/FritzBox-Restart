# FritzBox Restart

A simple, safe automation script to reboot your AVM FRITZ!Box router via its web interface using [Playwright](https://playwright.dev/).

> Tested with **FritzBox 7590** running **FritzOS 8.21**

---

## Features

- Automates the full reboot flow: login, navigation, reboot trigger, and confirmation
- Built-in safety confirmation before execution
- **Strict safety guards** -- only the "FRITZ!Box neu starten" card and the "Neu starten" confirmation button are ever clicked. Factory reset, backup, restore, and all other actions are never touched.
- Credentials stored securely in a local `.env` file (excluded from git)
- Clean, readable CLI output with step-by-step progress

## Prerequisites

- Python 3.8+
- A FRITZ!Box router accessible on your local network

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/FritzBox-Restart.git
cd FritzBox-Restart

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
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
| `FRITZBOX_URL` | No | `http://fritz.box` | URL of your FritzBox web interface |
| `FRITZBOX_USERNAME` | No | *(empty)* | Username (only needed if you configured multiple users) |

> **Note:** The `.env` file is excluded from version control via `.gitignore`. Never commit your credentials.

## Usage

```bash
python3 fritzbox_reboot.py
```

### Example Output

```
====================================================
  FritzBox Restart - Version 1.0
  Tested with FritzOS: 8.21
====================================================

  Are you sure you want to reboot your FritzBox? (yes/no): y

  -> Connecting to http://fritz.box ...
  -> Logging in ...
  -> Login successful.
  -> Navigating to System > Sicherung ...
  -> Looking for 'FRITZ!Box neu starten' card ...
  -> Clicking 'FRITZ!Box neu starten' ...
  -> Looking for confirmation button 'Neu starten' ...
  -> Confirming with 'Neu starten' ...

  [OK] FritzBox reboot triggered successfully.
  The router will restart now. This takes about 1-2 minutes.
```

## Safety

This script is designed with multiple layers of protection:

1. **User confirmation** -- You must type `yes` or `y` before anything happens
2. **Exact text matching** -- The script verifies the exact text content of every element before clicking
3. **Abort on mismatch** -- If any element text doesn't match expectations, the script aborts immediately
4. **No destructive actions** -- Factory reset, backup overwrite, and restore buttons are never interacted with

## How It Works

The script uses Playwright to automate a Chromium browser and performs the following steps:

1. Opens the FritzBox web interface
2. Logs in with the credentials from `.env`
3. Navigates to **System > Sicherung**
4. Clicks the **"FRITZ!Box neu starten"** card (with text verification)
5. Confirms the reboot by clicking **"Neu starten"** (with text verification)
6. Closes the browser

The router typically takes 1-2 minutes to restart.

## Compatibility

| FritzBox Model | FritzOS Version | Status |
|---|---|---|
| 7590 | 8.21 | Tested |

> Other FritzBox models with FritzOS 7.x+ may work but are untested. Contributions welcome!

## License

This project is licensed under the [MIT License](LICENSE).

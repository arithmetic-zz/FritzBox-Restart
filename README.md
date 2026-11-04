![FritzBox Restart](docs/readme_banner.png)

# FritzBox Restart

Current release: [v3.0.0](https://github.com/arithmetic-zz/FritzBox-Restart/releases/tag/v3.0.0)

A CLI tool to reboot your AVM FRITZ!Box router via the TR-064 API.

Use the API method for regular use. It sends the reboot command directly, avoiding browser startup, page navigation, and UI waits. Playwright is available for testing the web flow or watching the steps in a visible Chromium window.

Tested with FritzBox 7590 running FritzOS 8.21 / 8.25. Each script asks you to type `yes` or `y` before rebooting.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (manages Python and dependencies)
- Python 3.15.2 (installed automatically by uv)
- A FRITZ!Box router accessible on your local network

Enable TR-064 access in your FritzBox web interface:

Heimnetz > Netzwerk > Netzwerkeinstellungen > "Zugriff für Anwendungen zulassen"
(Home Network > Network > Network Settings > "Allow access for applications")

## Installation

```bash
# Clone the repository
git clone https://github.com/arithmetic-zz/FritzBox-Restart.git
cd FritzBox-Restart

# Install the pinned Python version and dependencies in .venv
uv sync --locked
```

Python is pinned in `.python-version`; `pyproject.toml` declares dependencies and `uv.lock` locks their versions. Run scripts with `uv run` to use the project environment.

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

The `.env` file stores your password in plain text. It is excluded from version control via `.gitignore`; never commit it.

## Usage

### API (recommended)

Send the reboot command via TR-064:

```bash
uv run python fritzbox_reboot.py --method api
```

Or run the API backend directly:

```bash
uv run python fritzbox_reboot_api.py
```

Run the main script without `--method` if you want to choose interactively:

```bash
uv run python fritzbox_reboot.py
```

### Standalone curl script

After a successful API reboot, you can save the reboot command as `reboot_fritzbox.sh`. The script uses `curl` with TR-064 SOAP and runs without Python. It also asks you to type `yes` or `y` before rebooting.

The generated script contains your password in plain text and is excluded from version control via `.gitignore`. Treat any copies as credentials.

```bash
./reboot_fritzbox.sh
```

<details>
<summary>Example output (API/TR-064)</summary>

```
====================================================
  FritzBox Restart (API/TR-064) - Version 3.0.0
  Tested with FritzOS: 8.21 / 8.25
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

</details>

## Playwright for tests and observation

Use this variant to test the web flow or watch the login, navigation, and reboot steps in a visible browser. It requires a German FritzBox interface and Chromium:

```bash
uv run playwright install chromium
uv run python fritzbox_reboot.py --method web
```

You can also run the web backend directly:

```bash
uv run python fritzbox_reboot_web.py
```

This flow sends a real reboot command after you confirm with `yes` or `y`.

<details>
<summary>Example output (Playwright)</summary>

```
====================================================
  FritzBox Restart (Web/Playwright) - Version 3.0.0
  Tested with FritzOS: 8.21 / 8.25
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

</details>

## How it works and safety checks

### API method (TR-064)

The API backend uses [fritzconnection](https://github.com/kbr/fritzconnection) to call `DeviceConfig1:Reboot` via TR-064 SOAP with HTTP Digest authentication.

The API backend calls only this reboot action.

### Web method (Playwright)

The web backend uses Playwright to:

1. Open the FritzBox web interface
2. Log in with the credentials from `.env`
3. Navigate to System > Sicherung (System > Backup)
4. Check and click the "FRITZ!Box neu starten" (restart FRITZ!Box) card
5. Check and click "Neu starten" (restart), if the confirmation button is present and visible
6. Close the browser

Before clicking the reboot card, the web backend checks that its text is exactly
`FRITZ!Box neu starten`. If a confirmation button is present and visible, it checks
for exactly `Neu starten` before clicking. It aborts if the reboot card is missing
or either text check fails. If no confirmation button is found, it reports that
the reboot may have been triggered directly.

The script does not click factory-reset, backup, or restore controls.

## Compatibility

| FritzBox Model | FritzOS Version | Status |
|---|---|---|
| 7590 | 8.21 | Tested |
| 7590 | 8.25 | Tested |

Other FritzBox models with FritzOS 7.x+ are untested.

## Development

### Dependencies

After changing dependencies with `uv add` or `uv remove`, regenerate the optional pip requirements file:

```bash
uv export --format requirements-txt --no-hashes --no-emit-project --output-file requirements.txt
```

### Checks

GitHub Actions runs the `Syntax and lint` check for every pull request targeting
`main` and every push to `main`. For changes limited to Markdown, images, and
`.gitignore`, it skips Python setup and checks. Otherwise, it compiles the Python
files and runs basic Ruff correctness checks. Manual runs always perform these
checks. It does not import or execute the reboot scripts, install the router/browser
dependencies, or require credentials or router access.

Run the same checks locally:

```bash
uv python install
uv run --no-project python -m py_compile *.py
uv tool run ruff==0.17.3 check .
```

## Release 3.0.0

- Python 3.15.2 managed by uv, with an isolated project environment.
- Reproducible dependencies in `uv.lock`, including Playwright 1.64.1 and python-dotenv 1.2.4.
- Repository guidance migrated from `CLAUDE.md` to `AGENTS.md`.

If you're upgrading from 2.0, the project now requires Python 3.15 or newer. Install uv and run `uv sync --locked`. Start the tool with `uv run python fritzbox_reboot.py --method api`. Keep your existing local `.env` file. Install Chromium only if you want to use Playwright.

## License

Licensed under the [MIT License](LICENSE).

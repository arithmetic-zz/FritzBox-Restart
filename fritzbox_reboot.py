#!/usr/bin/env python3
"""
FritzBox Reboot - Main Script.

Provides a choice between two reboot methods:
  - API (TR-064): Lightweight, no browser needed
  - Web (Playwright): Browser automation through the web interface

Usage:
    python3 fritzbox_reboot.py              # Interactive method selection
    python3 fritzbox_reboot.py --method api  # Use TR-064 API directly
    python3 fritzbox_reboot.py --method web  # Use Playwright directly
"""

import argparse
import sys

VERSION = "2.0"
TESTED_FRITZOS = "8.21"


def print_header():
    print()
    print("=" * 52)
    print(f"  FritzBox Restart - Version {VERSION}")
    print(f"  Tested with FritzOS: {TESTED_FRITZOS}")
    print("=" * 52)
    print()


def select_method() -> str:
    """Show interactive menu and return the chosen method."""
    print("  Reboot method:")
    print("    [1] API  (TR-064, lightweight, no browser needed)")
    print("    [2] Web  (Playwright, browser automation)")
    print()
    choice = input("  Select method (1/2): ").strip()
    if choice == "1":
        return "api"
    elif choice == "2":
        return "web"
    else:
        print(f"\n  [ERROR] Invalid choice: '{choice}'")
        sys.exit(1)


def run_api():
    """Run the TR-064 API reboot."""
    try:
        from fritzbox_reboot_api import (
            reboot_fritzbox,
            generate_curl_script,
            FRITZBOX_PASSWORD,
            env_path,
        )
        from fritzconnection.core.exceptions import (
            FritzConnectionException,
            FritzAuthorizationError,
        )
    except ImportError:
        print("\n  [ERROR] fritzconnection is not installed.")
        print("  Run: pip install fritzconnection")
        sys.exit(1)

    if not FRITZBOX_PASSWORD:
        print(f"  [ERROR] FRITZBOX_PASSWORD is not set.")
        print(f"  Please add your password to: {env_path}")
        sys.exit(1)

    try:
        reboot_fritzbox()

        save = input("  Save reboot command as standalone curl script? (yes/no): ").strip().lower()
        if save in ("yes", "y"):
            print()
            generate_curl_script()

    except FritzAuthorizationError:
        print("\n  [ERROR] Authentication failed.")
        print("  Please check your username and password in .env")
        sys.exit(1)
    except FritzConnectionException as e:
        print(f"\n  [ERROR] Connection failed: {e}")
        print("  Make sure TR-064 is enabled in your FritzBox:")
        print("  Heimnetz > Netzwerk > Netzwerkeinstellungen >")
        print('  "Zugriff fuer Anwendungen zulassen"')
        print("  (Home Network > Network > Network Settings > Allow access for applications)")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        sys.exit(1)


def run_web():
    """Run the Playwright web reboot."""
    try:
        from fritzbox_reboot_web import (
            reboot_fritzbox,
            FRITZBOX_PASSWORD,
            env_path,
        )
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
    except ImportError:
        print("\n  [ERROR] Playwright is not installed.")
        print("  Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    if not FRITZBOX_PASSWORD:
        print(f"  [ERROR] FRITZBOX_PASSWORD is not set.")
        print(f"  Please add your password to: {env_path}")
        sys.exit(1)

    try:
        reboot_fritzbox()
    except PlaywrightTimeout as e:
        print(f"\n  [ERROR] Timeout: {e}")
        print("  The FritzBox web interface did not respond in time.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reboot your FritzBox router.",
    )
    parser.add_argument(
        "--method",
        choices=["api", "web"],
        help="Reboot method: 'api' (TR-064) or 'web' (Playwright)",
    )
    args = parser.parse_args()

    print_header()

    method = args.method or select_method()

    print()
    answer = input("  Are you sure you want to reboot your FritzBox? (yes/no): ").strip().lower()
    if answer not in ("yes", "y"):
        print("  Aborted.")
        sys.exit(0)

    print()

    if method == "api":
        run_api()
    else:
        run_web()

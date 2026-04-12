#!/usr/bin/env python3
"""
FritzBox Reboot Script via Playwright (Web UI Automation).

Reads credentials from a .env file and performs a reboot of the
FritzBox router through its web interface using browser automation.

SAFETY: Only the "FRITZ!Box neu starten" (restart FRITZ!Box) card and
the "Neu starten" (restart) confirmation button are ever clicked.
No other buttons (factory reset, backup, restore, etc.) are touched
under any circumstances.

Can be used standalone or called from fritzbox_reboot.py.

Requirements:
    pip install playwright python-dotenv
    playwright install chromium
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

VERSION = "2.0"
TESTED_FRITZOS = "8.21 / 8.25"

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

FRITZBOX_URL = os.getenv("FRITZBOX_URL", "http://fritz.box")
FRITZBOX_USERNAME = os.getenv("FRITZBOX_USERNAME", "")
FRITZBOX_PASSWORD = os.getenv("FRITZBOX_PASSWORD", "")


def print_header():
    print()
    print("=" * 52)
    print(f"  FritzBox Restart (Web/Playwright) - Version {VERSION}")
    print(f"  Tested with FritzOS: {TESTED_FRITZOS}")
    print("=" * 52)
    print()


def step(msg: str):
    print(f"  -> {msg}")


def reboot_fritzbox():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(30000)

        # --- Login ---
        step(f"Connecting to {FRITZBOX_URL} ...")
        page.goto(FRITZBOX_URL)
        page.wait_for_load_state("networkidle")

        step("Logging in ...")
        username_field = page.locator('input[name="username"], #uiViewUser input[type="text"]')
        if FRITZBOX_USERNAME and username_field.count() > 0:
            username_field.first.fill(FRITZBOX_USERNAME)

        password_field = page.locator('input[type="password"]')
        password_field.first.fill(FRITZBOX_PASSWORD)

        login_button = page.locator('button[type="submit"], #submitLoginBtn, button:has-text("Anmelden")')
        login_button.first.click()

        page.wait_for_load_state("networkidle")
        time.sleep(3)

        if page.locator('input[type="password"]').count() > 0:
            print("\n  [ERROR] Login failed. Please check your password.")
            browser.close()
            sys.exit(1)

        step("Login successful.")

        # --- Navigate: System > Sicherung (System > Backup) ---
        step("Navigating to System > Sicherung (Backup) ...")
        page.locator('text="System"').first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        page.locator('text="Sicherung"').first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # --- ONLY click the "FRITZ!Box neu starten" card ---
        # SAFETY: Exact text match. Only this card, nothing else.
        REBOOT_CARD_TEXT = "FRITZ!Box neu starten"
        step(f"Looking for '{REBOOT_CARD_TEXT}' card ...")

        reboot_card = page.locator(f'text="{REBOOT_CARD_TEXT}"')
        if reboot_card.count() == 0:
            print(f"\n  [ERROR] Card '{REBOOT_CARD_TEXT}' not found.")
            browser.close()
            sys.exit(1)

        # Safety check: verify the element text
        card_text = reboot_card.first.text_content().strip()
        if card_text != REBOOT_CARD_TEXT:
            print(f"\n  [ERROR] Unexpected element text '{card_text}'. Aborting.")
            browser.close()
            sys.exit(1)

        reboot_card.first.scroll_into_view_if_needed()
        time.sleep(1)
        step(f"Clicking '{REBOOT_CARD_TEXT}' ...")
        reboot_card.first.click(force=True)
        time.sleep(3)

        # --- ONLY click the "Neu starten" confirmation button ---
        # SAFETY: Exact text match on the confirmation button.
        CONFIRM_TEXT = "Neu starten"
        step(f"Looking for confirmation button '{CONFIRM_TEXT}' ...")

        confirm_button = page.locator(f'button:has-text("{CONFIRM_TEXT}")')
        if confirm_button.count() > 0 and confirm_button.first.is_visible():
            btn_text = confirm_button.first.text_content().strip()
            if btn_text != CONFIRM_TEXT:
                print(f"\n  [ERROR] Unexpected button text '{btn_text}'. Aborting.")
                browser.close()
                sys.exit(1)

            step(f"Confirming with '{CONFIRM_TEXT}' ...")
            confirm_button.first.click(force=True)
        else:
            step("No confirmation dialog found. Reboot may have been triggered directly.")

        time.sleep(5)

        print()
        print("  [OK] FritzBox reboot triggered successfully.")
        print("  The router will restart now. This takes about 1-2 minutes.")
        print()
        browser.close()


if __name__ == "__main__":
    print_header()

    if not FRITZBOX_PASSWORD:
        print(f"  [ERROR] FRITZBOX_PASSWORD is not set.")
        print(f"  Please add your password to: {env_path}")
        sys.exit(1)

    answer = input("  Are you sure you want to reboot your FritzBox? (yes/no): ").strip().lower()
    if answer not in ("yes", "y"):
        print("  Aborted.")
        sys.exit(0)

    print()

    try:
        reboot_fritzbox()
    except PlaywrightTimeout as e:
        print(f"\n  [ERROR] Timeout: {e}")
        print("  The FritzBox web interface did not respond in time.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        sys.exit(1)

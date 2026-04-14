#!/usr/bin/env python3
"""
Spire Missouri East Rate Manager
Downloads, parses, and updates residential gas rates.

Usage:
    python3 spire_rate_manager.py [--download] [--parse] [--check]
"""

import argparse
import json
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import urlretrieve

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SPIRE_URLS = {
    "mo_east_tariff": "https://www.spireenergy.com/sites/default/files/2025-12/10242025-SpireMOTariff_0.pdf",
}

CACHE_DIR = Path(__file__).parent
CACHE_FILES = {
    "mo_east_tariff": CACHE_DIR / "10242025-SpireMOTariff_0.pdf",
}

RATE_CACHE_JSON = CACHE_DIR / "parsed_rates.json"

HA_SUPERVISOR_TOKEN_FILE = Path("/usr/share/hassio/homeassistant/token")
HA_API_URL = "http://supervisor/core/api"


class SpireRateParser:
    """Parse Spire Missouri East rate sheets from PDF files."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.text = self._extract_text()

    def _extract_text(self) -> str:
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(self.pdf_path), "-"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("Failed to extract text from %s: %s", self.pdf_path, e)
            return ""
        except FileNotFoundError:
            logger.error(
                "pdftotext not found. Install with: apt-get install poppler-utils"
            )
            return ""

    def parse_rates(self) -> Dict[str, Any]:
        """Parse gas rates from the extracted PDF text.

        Returns:
            Dictionary with effective_date, customer_charge, winter_rate, summer_rate, and pga_rate.
        """
        rates: Dict[str, Any] = {
            "effective_date": None,
            "customer_charge": None,
            "winter_rate": None,
            "summer_rate": None,
            "pga_rate": None,
        }

        date_match = re.search(r"Effective\s+(\d{1,2}/\d{1,2}/\d{4})", self.text)
        if date_match:
            rates["effective_date"] = date_match.group(1)

        customer_match = re.search(
            r"Customer\s+charge\s*\$?(\d+\.\d{2})", self.text, re.IGNORECASE
        )
        if customer_match:
            rates["customer_charge"] = float(customer_match.group(1))

        winter_match = re.search(
            r"Winter\s+billing\s*\(Nov\.\s*-\s*Apr\.\)\s*\$?(\d+\.\d{5})\s*per\s*Ccf",
            self.text,
            re.IGNORECASE,
        )
        if winter_match:
            rates["winter_rate"] = float(winter_match.group(1))

        summer_match = re.search(
            r"Summer\s+billing\s*\(May\s*-\s*Oct\.\)\s*\$?(\d+\.\d{5})\s*per\s*Ccf",
            self.text,
            re.IGNORECASE,
        )
        if summer_match:
            rates["summer_rate"] = float(summer_match.group(1))

        pga_match = re.search(
            r"Purchased\s+Gas\s+Adjustment\s*\(PGA\)\s*:\s*\$?(\d+\.\d{5})\s*per\s*Ccf",
            self.text,
            re.IGNORECASE,
        )
        if pga_match:
            rates["pga_rate"] = float(pga_match.group(1))

        return rates


class SpireRateManager:
    """Manage Spire Missouri East rates: download, parse, and update Home Assistant."""

    def __init__(self, force_download: bool = False):
        """Initialize the rate manager.

        Args:
            force_download: Whether to force redownload of PDFs.
        """
        self.force_download = force_download
        self.rates: Optional[Dict[str, Any]] = None

    def download_pdfs(self) -> bool:
        """Download latest rate PDFs from Spire Energy.

        Returns:
            True if all downloads succeeded, False otherwise.
        """
        success = True
        for name, url in SPIRE_URLS.items():
            cache_file = CACHE_FILES[name]
            if cache_file.exists() and not self.force_download:
                logger.info("Using cached %s PDF: %s", name, cache_file)
                continue
            try:
                logger.info("Downloading %s PDF from %s", name, url)
                urlretrieve(url, cache_file)
                logger.info("Downloaded %s", cache_file)
            except URLError as e:
                logger.error("Failed to download %s: %s", url, e)
                success = False
            except (IOError, OSError) as e:
                logger.error("Unexpected error downloading %s: %s", url, e)
                success = False
        return success

    def parse_rates(self) -> Optional[Dict[str, Any]]:
        """Parse rates from cached PDF and save to JSON.

        Returns:
            Dictionary with parsed rates or None if parsing failed.
        """
        pdf_path = CACHE_FILES["mo_east_tariff"]
        if not pdf_path.exists():
            logger.error("Spire tariff PDF not found: %s", pdf_path)
            return None
        parser = SpireRateParser(pdf_path)
        self.rates = parser.parse_rates()
        with open(RATE_CACHE_JSON, "w", encoding="utf-8") as f:
            json.dump(self.rates, f, indent=2)
        logger.info("Cached parsed rates to %s", RATE_CACHE_JSON)
        return self.rates

    def load_cached_rates(self) -> Optional[Dict[str, Any]]:
        """Load previously parsed rates from cache file.

        Returns:
            Dictionary with cached rates or None if cache doesn't exist.
        """
        if RATE_CACHE_JSON.exists():
            with open(RATE_CACHE_JSON, "r", encoding="utf-8") as f:
                self.rates = json.load(f)
            logger.info("Loaded cached rates from %s", RATE_CACHE_JSON)
            return self.rates
        return None

    def update_home_assistant(self, dry_run: bool = True) -> bool:
        """Update Home Assistant input_number entities with parsed rates.

        Maps parsed rates to Home Assistant input_number helpers and updates them
        via the Home Assistant Core API using supervisor authentication.

        Args:
            dry_run: If True, log updates without writing to HA. Default is True.

        Returns:
            True if update succeeded or dry_run is True, False otherwise.

        Raises:
            ImportError: If requests library is not available.
        """
        if not self.rates:
            logger.error("No rates loaded")
            return False

        updates = {
            "input_number.spire_mo_east_monthly_fixed": self.rates.get(
                "customer_charge"
            ),
            "input_number.spire_mo_east_winter_rate": self.rates.get("winter_rate"),
            "input_number.spire_mo_east_summer_rate": self.rates.get("summer_rate"),
            "input_number.spire_mo_east_pga_rate": self.rates.get("pga_rate"),
        }

        if dry_run:
            logger.info("DRY RUN - Would update Home Assistant with:")
            for entity, value in updates.items():
                logger.info("  %s = %s", entity, value)
            return True

        try:
            with open(HA_SUPERVISOR_TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            for entity_id, value in updates.items():
                url = f"{HA_API_URL}/states/{entity_id}"
                data = {
                    "state": str(value),
                    "attributes": {
                        "updated_by": "spire_rate_manager",
                        "last_update": datetime.now().isoformat(),
                    },
                }
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.status_code in [200, 201]:
                    logger.info("Updated %s = %s", entity_id, value)
                else:
                    logger.error(
                        "Failed to update %s: %s", entity_id, response.status_code
                    )
                    return False
            return True
        except ImportError:
            logger.error(
                "requests library not available. Install with: pip install requests"
            )
            return False
        except (IOError, OSError) as e:
            logger.error("Error updating Home Assistant entities: %s", e)
            return False

    def print_rate_summary(self) -> None:
        """Print parsed rates to log."""
        if not self.rates:
            logger.error("No rates loaded")
            return
        logger.info("SPIRE MISSOURI EAST RESIDENTIAL RATES")
        logger.info("Effective Date: %s", self.rates.get("effective_date"))
        logger.info("Customer Charge: $%.2f/month", self.rates.get("customer_charge"))
        logger.info("Winter Rate (Nov-Apr): $%.5f/ccf", self.rates.get("winter_rate"))
        logger.info("Summer Rate (May-Oct): $%.5f/ccf", self.rates.get("summer_rate"))
        logger.info("PGA: $%.5f/ccf", self.rates.get("pga_rate"))


def main() -> None:
    """Main entry point for rate manager CLI."""
    parser = argparse.ArgumentParser(description="Spire Missouri East Rate Manager")
    parser.add_argument("--download", action="store_true", help="Download latest PDF")
    parser.add_argument("--parse", action="store_true", help="Parse rates from PDF")
    parser.add_argument("--check", action="store_true", help="Display parsed rates")
    parser.add_argument("--update", action="store_true", help="Update HA helpers")
    parser.add_argument(
        "--dry-run", action="store_true", help="Do not write updates to HA"
    )
    parser.add_argument("--force-download", action="store_true", help="Redownload PDF")
    args = parser.parse_args()

    manager = SpireRateManager(force_download=args.force_download)

    if args.download:
        manager.download_pdfs()

    if args.parse:
        manager.parse_rates()

    if args.check:
        if not manager.rates:
            manager.load_cached_rates()
        manager.print_rate_summary()

    if args.update:
        if not manager.rates:
            manager.load_cached_rates()
        manager.update_home_assistant(dry_run=args.dry_run)

    if not any([args.download, args.parse, args.check, args.update]):
        parser.print_help()


if __name__ == "__main__":
    main()

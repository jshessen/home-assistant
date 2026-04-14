#!/usr/bin/env python3
"""
Ameren Missouri Rate Manager
Automatically downloads, parses, and updates residential electricity rates.

This script:
1. Downloads PDF rate sheets from Ameren Missouri
2. Extracts rate information using pdftotext
3. Determines current season and applicable rates
4. Updates Home Assistant input_number helpers
5. Sends notifications when rates change

Usage:
    python3 ameren_rate_manager.py [--update] [--check] [--force-download]
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import urlretrieve
from urllib.error import URLError

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
AMEREN_URLS = {
    "toc": "https://www.ameren.com/-/media/rates/missouri/residential/electric-rates/rates/uecsheet53tocrates.ashx",
    "residential": "https://www.ameren.com/-/media/rates/missouri/residential/electric-rates/rates/uecsheet54rate1mres.ashx",
    "misc_charges": "https://www.ameren.com/-/media/rates/missouri/residential/electric-rates/rates/uecsheet63miscchgs.ashx",
}

CACHE_DIR = Path(__file__).parent
CACHE_FILES = {
    "toc": CACHE_DIR / "UECSheet53TOCRates.pdf",
    "residential": CACHE_DIR / "UECSheet54Rate1MRES.pdf",
    "misc_charges": CACHE_DIR / "UECSheet63MiscChgs.pdf",
}

RATE_CACHE_JSON = CACHE_DIR / "parsed_rates.json"

# Home Assistant API Configuration
HA_CONFIG_DIR = Path(__file__).parent.parent.parent
HA_SUPERVISOR_TOKEN_FILE = Path("/usr/share/hassio/homeassistant/token")
HA_API_URL = "http://supervisor/core/api"


class AmerenRateParser:
    """Parse Ameren Missouri rate sheets from PDF files."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.text = self._extract_text()

    def _extract_text(self) -> str:
        """Extract text from PDF using pdftotext."""
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

    def parse_residential_rates(self) -> Dict[str, Any]:
        """Parse Rate 1(M) residential rates from PDF text."""
        rates: Dict[str, Any] = {
            "effective_date": None,
            "summer": {
                "customer_charge": None,
                "low_income_charge": None,
                "energy_rate": None,
            },
            "winter": {
                "customer_charge": None,
                "low_income_charge": None,
                "tier1_kwh_limit": None,
                "tier1_rate": None,
                "tier2_rate": None,
            },
        }

        # Extract effective date
        date_match = re.search(r"DATE EFFECTIVE\s+(\w+ \d+, \d{4})", self.text)
        if date_match:
            rates["effective_date"] = date_match.group(1)

        # Extract summer rates (June - September)
        summer_section = re.search(
            r"Summer Rate.*?Customer Charge.*?\$(\d+\.\d{2}).*?"
            r"Low-Income.*?\$(\d+\.\d{2}).*?"
            r"Energy Charge.*?(\d+\.\d{2})¢",
            self.text,
            re.DOTALL,
        )
        if summer_section:
            rates["summer"]["customer_charge"] = float(summer_section.group(1))
            rates["summer"]["low_income_charge"] = float(summer_section.group(2))
            rates["summer"]["energy_rate"] = float(summer_section.group(3)) / 100.0

        # Extract winter rates (October - May) with tiered pricing
        winter_section = re.search(
            r"Winter Rate.*?Customer Charge.*?\$(\d+\.\d{2}).*?"
            r"Low-Income.*?\$(\d+\.\d{2}).*?"
            r"First (\d+) kWh.*?(\d+\.\d{2})¢.*?"
            r"Over \d+ kWh.*?(\d+\.\d{2})¢",
            self.text,
            re.DOTALL,
        )
        if winter_section:
            rates["winter"]["customer_charge"] = float(winter_section.group(1))
            rates["winter"]["low_income_charge"] = float(winter_section.group(2))
            rates["winter"]["tier1_kwh_limit"] = int(winter_section.group(3))
            rates["winter"]["tier1_rate"] = float(winter_section.group(4)) / 100.0
            rates["winter"]["tier2_rate"] = float(winter_section.group(5)) / 100.0

        return rates


class AmerenRateManager:
    """Manage Ameren Missouri rate downloads, parsing, and HA integration."""

    def __init__(self, force_download: bool = False):
        self.force_download = force_download
        self.rates: Optional[Dict[str, Any]] = None

    def download_pdfs(self) -> bool:
        """Download PDF rate sheets from Ameren."""
        success = True
        for name, url in AMEREN_URLS.items():
            cache_file = CACHE_FILES[name]

            # Skip if cached and not forcing download
            if cache_file.exists() and not self.force_download:
                logger.info("Using cached %s PDF: %s", name, cache_file)
                continue

            logger.info("Downloading %s PDF from %s", name, url)
            try:
                urlretrieve(url, cache_file)
                logger.info("Downloaded %s", cache_file)
            except URLError as e:
                logger.error("Failed to download %s: %s", url, e)
                success = False
            except (OSError, IOError) as e:
                logger.error("Unexpected error downloading %s: %s", url, e)
                success = False

        return success

    def parse_rates(self) -> Optional[Dict[str, Any]]:
        """Parse all downloaded rate PDFs."""
        residential_pdf = CACHE_FILES["residential"]

        if not residential_pdf.exists():
            logger.error("Residential rate PDF not found: %s", residential_pdf)
            return None

        parser = AmerenRateParser(residential_pdf)
        self.rates = parser.parse_residential_rates()

        # Cache parsed rates
        with open(RATE_CACHE_JSON, "w", encoding="utf-8") as f:
            json.dump(self.rates, f, indent=2)
        logger.info("Cached parsed rates to %s", RATE_CACHE_JSON)

        return self.rates

    def load_cached_rates(self) -> Optional[Dict[str, Any]]:
        """Load previously parsed rates from cache."""
        if RATE_CACHE_JSON.exists():
            with open(RATE_CACHE_JSON, "r", encoding="utf-8") as f:
                self.rates = json.load(f)
            logger.info("Loaded cached rates from %s", RATE_CACHE_JSON)
            return self.rates
        return None

    def get_current_season(self) -> str:
        """Determine current billing season (summer/winter)."""
        month = datetime.now().month
        # Summer: June (6) through September (9)
        # Winter: October (10) through May (5)
        if 6 <= month <= 9:
            return "summer"
        else:
            return "winter"

    def calculate_effective_rate(
        self, consumption_kwh: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate effective rate based on current season and consumption.

        Returns dict with:
            - season: 'summer' or 'winter'
            - customer_charge: monthly fixed charge
            - energy_rate: effective $/kWh rate
            - total_cost: estimated bill for given consumption
        """
        if not self.rates:
            logger.error("No rates loaded. Run parse_rates() first.")
            return None

        season = self.get_current_season()
        season_rates = self.rates[season]

        result: Dict[str, Any] = {
            "season": season,
            "customer_charge": float(season_rates["customer_charge"]),
            "low_income_charge": float(season_rates.get("low_income_charge", 0.0)),
            "energy_rate": (
                None if season != "summer" else float(season_rates["energy_rate"])
            ),
            "energy_cost": None,
            "total_cost": None,
        }

        if season == "summer":
            # Summer: flat rate
            result["energy_rate"] = season_rates["energy_rate"]
            result["energy_cost"] = consumption_kwh * season_rates["energy_rate"]
        else:
            # Winter: tiered pricing
            tier1_limit = season_rates["tier1_kwh_limit"]
            tier1_rate = season_rates["tier1_rate"]
            tier2_rate = season_rates["tier2_rate"]

            if consumption_kwh <= tier1_limit:
                result["energy_rate"] = tier1_rate
                result["energy_cost"] = consumption_kwh * tier1_rate
            else:
                # Mixed tier consumption
                tier1_cost = tier1_limit * tier1_rate
                tier2_kwh = consumption_kwh - tier1_limit
                tier2_cost = tier2_kwh * tier2_rate
                result["energy_cost"] = tier1_cost + tier2_cost
                # Effective blended rate
                result["energy_rate"] = result["energy_cost"] / consumption_kwh

        result["total_cost"] = (
            result["customer_charge"]
            + result["low_income_charge"]
            + result["energy_cost"]
        )

        return result

    def update_home_assistant(self, dry_run: bool = False) -> bool:
        """
        Update Home Assistant input_number helpers with current rates.

        Sets input_number values based on current season and average consumption.
        """
        if not self.rates:
            logger.error("No rates available to update Home Assistant")
            return False

        season = self.get_current_season()

        # For average monthly consumption, use a reasonable estimate
        # User can adjust based on their actual usage
        avg_consumption = 750 if season == "winter" else 900  # kWh

        effective = self.calculate_effective_rate(avg_consumption)
        if not effective:
            logger.error("Failed to calculate effective rate for updates")
            return False

        updates = {
            "input_number.ameren_mo_kwh_rate": effective["energy_rate"],
            "input_number.ameren_mo_monthly_fixed": (
                effective["customer_charge"] + effective["low_income_charge"]
            ),
        }

        logger.info("Current season: %s", season.upper())
        logger.info(
            "Effective rate for %d kWh: $%.4f/kWh",
            avg_consumption,
            effective["energy_rate"],
        )
        logger.info(
            "Fixed charges: $%.2f/month",
            updates["input_number.ameren_mo_monthly_fixed"],
        )

        if dry_run:
            logger.info("DRY RUN - Would update Home Assistant with:")
            for entity, value in updates.items():
                logger.info("  %s = %s", entity, value)
            return True

        # Update HA entities (requires HA REST API access)
        success = self._update_ha_entities(updates)
        return success

    def _update_ha_entities(self, updates: Dict[str, float]) -> bool:
        """Update Home Assistant entities via REST API."""
        # Check if running inside HA supervisor environment
        if not HA_SUPERVISOR_TOKEN_FILE.exists():
            logger.warning(
                "Not running in HA Supervisor environment. "
                "Cannot auto-update entities. Use --dry-run to see values."
            )
            return False

        try:
            with open(HA_SUPERVISOR_TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            for entity_id, value in updates.items():
                url = f"{HA_API_URL}/states/{entity_id}"
                data: Dict[str, Any] = {
                    "state": str(value),
                    "attributes": {
                        "unit_of_measurement": (
                            "$/kWh" if "kwh_rate" in entity_id else "$"
                        ),
                        "updated_by": "ameren_rate_manager",
                        "last_update": datetime.now().isoformat(),
                    },
                }  # type: Dict[str, Any]

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

    def print_rate_summary(self):
        """Print formatted summary of current rates."""
        if not self.rates:
            logger.error("No rates loaded")
            return

        print("\n" + "=" * 70)
        print("AMEREN MISSOURI RESIDENTIAL RATES (1M)")
        print("=" * 70)

        if self.rates.get("effective_date"):
            print(f"Effective Date: {self.rates['effective_date']}")

        print("\n--- SUMMER RATES (June - September) ---")
        summer = self.rates["summer"]
        print(f"  Customer Charge:       ${summer['customer_charge']:.2f}/month")
        print(f"  Low-Income Charge:     ${summer['low_income_charge']:.2f}/month")
        print(
            f"  Energy Rate:           ${summer['energy_rate']:.4f}/kWh ({summer['energy_rate']*100:.2f}¢)"
        )

        print("\n--- WINTER RATES (October - May) ---")
        winter = self.rates["winter"]
        print(f"  Customer Charge:       ${winter['customer_charge']:.2f}/month")
        print(f"  Low-Income Charge:     ${winter['low_income_charge']:.2f}/month")
        print("  Energy Rate (Tiered):")
        print(
            f"    First {winter['tier1_kwh_limit']} kWh:    ${winter['tier1_rate']:.4f}/kWh ({winter['tier1_rate']*100:.2f}¢)"
        )
        print(
            f"    Over {winter['tier1_kwh_limit']} kWh:     ${winter['tier2_rate']:.4f}/kWh ({winter['tier2_rate']*100:.2f}¢)"
        )

        # Show current season effective rate
        season = self.get_current_season()
        print(f"\n--- CURRENT SEASON: {season.upper()} ---")

        # Calculate for example consumption levels
        examples = [500, 750, 1000, 1500]
        print("\nEstimated Monthly Bills:")
        for kwh in examples:
            calc = self.calculate_effective_rate(kwh)
            if not calc:
                logger.error("Failed to calculate effective rate for summary")
                return
            print(
                f"  {kwh:4d} kWh: ${calc['total_cost']:6.2f} "
                f"(${calc['energy_rate']:.4f}/kWh effective)"
            )

        print("=" * 70 + "\n")


def main():
    """Main CLI entry point for Ameren rate manager."""
    parser = argparse.ArgumentParser(
        description="Ameren Missouri Rate Manager for Home Assistant"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download latest PDFs from Ameren (default: use cached)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force re-download even if PDFs exist",
    )
    parser.add_argument(
        "--parse", action="store_true", help="Parse PDFs and extract rates"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update Home Assistant input_number helpers",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--check", action="store_true", help="Check current rates and show summary"
    )

    args = parser.parse_args()

    # Default action: check rates
    if not any(
        [args.download, args.parse, args.update, args.check, args.force_download]
    ):
        args.check = True

    manager = AmerenRateManager(force_download=args.force_download)

    # Download PDFs
    if args.download or args.force_download:
        if not manager.download_pdfs():
            logger.error("Failed to download one or more PDFs")
            return 1

    # Parse rates
    if args.parse or args.download or args.force_download:
        rates = manager.parse_rates()
        if not rates:
            logger.error("Failed to parse rates")
            return 1
    else:
        # Load from cache
        rates = manager.load_cached_rates()
        if not rates:
            logger.warning("No cached rates found. Run with --parse to parse PDFs.")
            return 1

    # Update Home Assistant
    if args.update:
        success = manager.update_home_assistant(dry_run=args.dry_run)
        if not success:
            logger.error("Failed to update Home Assistant")
            return 1

    # Display rate summary
    if args.check or args.parse:
        manager.print_rate_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())

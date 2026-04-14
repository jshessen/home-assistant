#!/usr/bin/env python3
"""
Alexa Orphan Device Cleanup Tool

Identifies and removes orphaned devices from Alexa Smart Home skill.
Orphaned devices are entities that Alexa still knows about, but Home Assistant
no longer exposes or should not expose (e.g., due to exclude patterns).

Usage:
    python3 alexa_orphan_cleanup.py
    python3 alexa_orphan_cleanup.py --har ~/Downloads/developer.amazon.com.har
    python3 alexa_orphan_cleanup.py --nuclear
    python3 alexa_orphan_cleanup.py --har file.har --auto-delete

Author: Home Assistant Setup
Version: 2.0.0
"""

import argparse
import fnmatch
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# Configuration
CONFIG_DIR = Path("/config")
ALEXA_CONFIG = CONFIG_DIR / "alexa.yaml"
ALEXA_EXCLUDE_DIR = CONFIG_DIR / "alexa" / "exclude"
STORAGE_DIR = CONFIG_DIR / ".storage"
ENTITY_REGISTRY = STORAGE_DIR / "core.entity_registry"
ALEXA_AUTH = STORAGE_DIR / "alexa_auth"
OUTPUT_DIR = CONFIG_DIR / "scripts"
HA_URL = "http://localhost:8123"
BATCH_SIZE = 50  # Devices per DeleteReport batch


def print_header(text, width=70):
    """Print a formatted header."""
    print(f"\n{'═' * width}")
    print(f"║{text.center(width - 2)}║")
    print(f"{'═' * width}\n")


def print_section(text, width=70):
    """Print a section header."""
    print(f"\n{'─' * width}")
    print(f"  {text}")
    print(f"{'─' * width}\n")


def log(level, message):
    """Print a log message with level."""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "PROGRESS": "\033[96m",
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"{color}[{level}]{reset} {message}")


def extract_devices_from_har(har_path):
    """Extract Alexa devices from HAR file."""
    try:
        with open(har_path, "r", encoding="utf-8") as f:
            har_data = json.load(f)

        # Find the API response with device data
        for entry in har_data["log"]["entries"]:
            if "/api/endpoints/ask" in entry["request"]["url"]:
                response_text = entry["response"]["content"].get("text", "")
                if response_text:
                    data = json.loads(response_text)
                    endpoints = data.get("endpoints", [])
                    devices = {}
                    for endpoint in endpoints:
                        entity_id = endpoint.get("endpointId", "")
                        friendly_name = endpoint.get("friendlyName", "")
                        devices[entity_id] = friendly_name
                    return devices

        log("ERROR", "Could not find device data in HAR file")
        return None

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        log("ERROR", f"Error processing HAR file: {e}")
        return None


def get_ha_exposed_entities():
    """Get list of entities currently exposed to Alexa by Home Assistant."""
    exposed_entities = set()

    # Try REST API first
    try:
        response = requests.get(f"{HA_URL}/api/states", timeout=5)
        if response.status_code == 200:
            all_entities = {entity["entity_id"]: entity for entity in response.json()}
            log("INFO", f"Loaded {len(all_entities)} entities from Home Assistant API")
        else:
            raise requests.RequestException("API unavailable")
    except (requests.RequestException, requests.Timeout):
        # Fallback to entity registry file
        log("INFO", "API unavailable, reading entity registry file...")
        try:
            with open(ENTITY_REGISTRY, "r", encoding="utf-8") as f:
                registry = json.load(f)
            all_entities = {e["entity_id"]: e for e in registry.get("entities", [])}
            log("INFO", f"Loaded {len(all_entities)} entities from registry")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            log("ERROR", f"Could not load entities: {e}")
            return None

    # Parse alexa.yaml to determine exposed domains
    try:
        with open(ALEXA_CONFIG, "r", encoding="utf-8") as f:
            alexa_config = f.read()

        # Extract included domains (simple parsing)
        included_domains = []
        in_filter_section = False
        for line in alexa_config.split("\n"):
            if "filter:" in line or "include_domains:" in line:
                in_filter_section = True
            elif in_filter_section and line.strip().startswith("-"):
                domain = line.strip().lstrip("-").strip()
                if domain and not domain.startswith("#"):
                    included_domains.append(domain)
            elif (
                in_filter_section and not line.strip().startswith("-") and line.strip()
            ):
                in_filter_section = False

        log("INFO", f"Found {len(included_domains)} included domains in alexa.yaml")

    except (FileNotFoundError, IOError) as e:
        log("WARNING", f"Could not parse alexa.yaml: {e}")
        # Use common defaults
        included_domains = [
            "light",
            "switch",
            "cover",
            "lock",
            "climate",
            "fan",
            "media_player",
            "scene",
            "script",
            "input_boolean",
        ]
        log("INFO", f'Using default domains: {", ".join(included_domains)}')

    # Load exclude patterns
    exclude_patterns = []
    if ALEXA_EXCLUDE_DIR.exists():
        for exclude_file in ALEXA_EXCLUDE_DIR.glob("*.yml"):
            try:
                with open(exclude_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and line.startswith("-"):
                            pattern = line.lstrip("-").strip()
                            exclude_patterns.append(pattern)
            except (FileNotFoundError, IOError) as e:
                log("WARNING", f"Could not read {exclude_file}: {e}")

        if exclude_patterns:
            log(
                "INFO",
                f"Loaded {len(exclude_patterns)} exclude patterns from alexa/exclude/",
            )

    # Filter entities
    for entity_id in all_entities:
        domain = entity_id.split(".")[0]

        # Check if domain is included
        if domain not in included_domains:
            continue

        # Check exclude patterns (basic glob matching)
        excluded = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(entity_id, pattern):
                excluded = True
                break

        if not excluded:
            exposed_entities.add(entity_id)

    return exposed_entities, len(exclude_patterns)


def identify_orphans(alexa_devices, ha_exposed):
    """Identify devices that are orphaned."""
    alexa_entity_ids = set(alexa_devices.keys())
    orphans = alexa_entity_ids - ha_exposed
    return orphans


def load_oauth_token():
    """Load OAuth token from Home Assistant storage."""
    try:
        with open(ALEXA_AUTH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Find the Alexa integration's token
        token_data = data.get("data", {})
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 0)

        if access_token:
            log("SUCCESS", f"Loaded access token (expires in {expires_in} seconds)")
            return access_token

        log("ERROR", "No access token found in storage")
        return None

    except FileNotFoundError:
        log("ERROR", f"OAuth storage file not found: {ALEXA_AUTH}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        log("ERROR", f"Error loading OAuth token: {e}")
        return None


def send_delete_report(entity_ids, _access_token):
    """Send DeleteReport events to Alexa via Home Assistant's integration."""
    # Use Home Assistant's built-in Alexa integration
    # This leverages the async_send_delete_message function

    deleted_count = 0
    failed_count = 0

    # Process in batches
    batches = [
        entity_ids[i : i + BATCH_SIZE] for i in range(0, len(entity_ids), BATCH_SIZE)
    ]

    log("INFO", f"Sending DeleteReport events in batches of {BATCH_SIZE}...")

    for i, batch in enumerate(batches, 1):
        log("PROGRESS", f"Batch {i}/{len(batches)}: {len(batch)} devices")

        # Call Home Assistant service to delete devices
        # The service will use the Alexa integration's built-in delete functionality
        try:
            response = requests.post(
                f"{HA_URL}/api/services/python_script/alexa_delete_devices",
                json={"entity_ids": list(batch)},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                deleted_count += len(batch)
            else:
                log("WARNING", f"Batch {i} failed with status {response.status_code}")
                failed_count += len(batch)

        except (requests.RequestException, requests.Timeout) as e:
            log("ERROR", f"Batch {i} failed: {e}")
            failed_count += len(batch)

    return deleted_count, failed_count


def save_report(alexa_devices, ha_exposed, orphans, exclude_count):
    """Save detailed report to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"alexa_orphan_report_{timestamp}.txt"
    orphan_file = OUTPUT_DIR / "alexa_orphans.txt"

    # Categorize orphans
    deleted_entities = []
    excluded_entities = []

    for entity_id in orphans:
        # Simple heuristic: if entity matches common exclude patterns, mark as excluded
        # Otherwise, consider it deleted
        if any(
            keyword in entity_id
            for keyword in ["_code_slot_", "_battery", "_rssi", "_last_seen"]
        ):
            excluded_entities.append(entity_id)
        else:
            deleted_entities.append(entity_id)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ALEXA ORPHAN DEVICE CLEANUP REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total devices in Alexa:            {len(alexa_devices)}\n")
        f.write(f"Currently exposed by HA:           {len(ha_exposed)}\n")
        f.write(f"Orphaned devices:                  {len(orphans)}\n")
        f.write(f"  - Deleted/renamed in HA:         {len(deleted_entities)}\n")
        f.write(f"  - Excluded by patterns:          {len(excluded_entities)}\n")
        f.write(f"Exclude patterns loaded:           {exclude_count}\n\n")

        f.write("ORPHANED DEVICES (Deleted/Renamed)\n")
        f.write("-" * 70 + "\n")
        for entity_id in sorted(deleted_entities)[:50]:  # First 50
            friendly_name = alexa_devices.get(entity_id, "Unknown")
            f.write(f"- {entity_id:<50} {friendly_name}\n")
        if len(deleted_entities) > 50:
            f.write(f"\n... and {len(deleted_entities) - 50} more\n")

        f.write("\n\nORPHANED DEVICES (Excluded by Patterns)\n")
        f.write("-" * 70 + "\n")
        for entity_id in sorted(excluded_entities)[:50]:  # First 50
            friendly_name = alexa_devices.get(entity_id, "Unknown")
            f.write(f"- {entity_id:<50} {friendly_name}\n")
        if len(excluded_entities) > 50:
            f.write(f"\n... and {len(excluded_entities) - 50} more\n")

        f.write("\n\n" + "=" * 70 + "\n")
        f.write("For full list, see: alexa_orphans.txt\n")
        f.write("=" * 70 + "\n")

    # Save simple list
    with open(orphan_file, "w", encoding="utf-8") as f:
        for entity_id in sorted(orphans):
            f.write(f"{entity_id}\n")

    log("SUCCESS", f"Report saved: {report_file}")
    log("INFO", f"Orphan list: {orphan_file}")

    return report_file


def nuclear_option():
    """Delete ALL devices and rediscover."""
    log(
        "WARNING",
        "NUCLEAR OPTION: This will delete ALL Home Assistant devices from Alexa",
    )
    confirm = input('\nType "DELETE ALL" to confirm: ')

    if confirm != "DELETE ALL":
        log("INFO", "Cancelled")
        return

    log("INFO", "Requesting device list from Home Assistant API...")

    try:
        response = requests.get(f"{HA_URL}/api/states", timeout=5)
        if response.status_code != 200:
            log("ERROR", "Could not fetch devices from Home Assistant")
            return

        all_entities = [e["entity_id"] for e in response.json()]
        log("INFO", f"Found {len(all_entities)} total entities")

        # Load token
        token = load_oauth_token()
        if not token:
            log("ERROR", "Could not load OAuth token")
            return

        # Send delete report
        log("INFO", "Sending DeleteReport for all devices...")
        deleted, failed = send_delete_report(all_entities, token)

        log("SUCCESS", f"Deleted {deleted} devices")
        if failed > 0:
            log("WARNING", f"{failed} deletions failed")

        log("INFO", "\nNow trigger Alexa discovery:")
        log("INFO", "  1. Open Alexa app")
        log("INFO", "  2. Devices → + → Add Device")
        log("INFO", '  3. Select "Home Assistant"')
        log("INFO", "  4. Discover devices")

    except (requests.RequestException, requests.Timeout) as e:
        log("ERROR", f"Nuclear option failed: {e}")


def main():
    """Main entry point for the Alexa Orphan Cleanup Tool."""
    parser = argparse.ArgumentParser(
        description="Alexa Orphan Device Cleanup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 alexa_orphan_cleanup.py
  python3 alexa_orphan_cleanup.py --har ~/Downloads/developer.amazon.com.har
  python3 alexa_orphan_cleanup.py --nuclear
  python3 alexa_orphan_cleanup.py --har file.har --auto-delete
        """,
    )
    parser.add_argument("--har", help="Path to HAR file from Amazon Developer Console")
    parser.add_argument(
        "--nuclear", action="store_true", help="Delete ALL devices and rediscover"
    )
    parser.add_argument(
        "--auto-delete",
        action="store_true",
        help="Automatically delete orphans without confirmation",
    )

    args = parser.parse_args()

    print_header("🧹 Alexa Orphan Device Cleanup Tool 🧹")

    # Nuclear option
    if args.nuclear:
        nuclear_option()
        return

    # Get HAR file
    har_path = args.har
    if not har_path:
        log("INFO", "Please provide a HAR file from Amazon Developer Console")
        log("INFO", "Instructions:")
        log("INFO", "  1. Open browser Developer Tools (F12)")
        log("INFO", "  2. Go to Network tab")
        log(
            "INFO",
            "  3. Navigate to: https://developer.amazon.com/alexa/console/ask/devices/",
        )
        log("INFO", "  4. Wait for page to load completely")
        log("INFO", "  5. Right-click in Network tab → Save all as HAR")
        log("INFO", "")
        har_path = input("Enter path to HAR file: ").strip()

    if not os.path.exists(har_path):
        log("ERROR", f"HAR file not found: {har_path}")
        return

    # Extract devices from HAR
    log("INFO", f"Processing HAR file: {har_path}")
    alexa_devices = extract_devices_from_har(har_path)
    if not alexa_devices:
        log("ERROR", "Could not extract devices from HAR file")
        return

    log("SUCCESS", f"Found {len(alexa_devices)} devices in Alexa")

    # Get currently exposed entities
    log("INFO", "Extracting currently exposed devices from Home Assistant...")
    result = get_ha_exposed_entities()
    if result is None:
        log("ERROR", "Could not determine exposed devices")
        return

    ha_exposed, exclude_count = result
    excluded_count = len(alexa_devices) - len(ha_exposed)  # Rough estimate
    log(
        "SUCCESS",
        f"Found {len(ha_exposed)} devices currently exposed by Home Assistant "
        f"(excluded {excluded_count})",
    )

    # Identify orphans
    log("INFO", "Identifying orphaned devices...")
    orphans = identify_orphans(alexa_devices, ha_exposed)

    if not orphans:
        log("SUCCESS", "No orphaned devices found! 🎉")
        return

    log("WARNING", f"Found {len(orphans)} orphaned devices")

    # Print summary
    print_header("ORPHAN ANALYSIS RESULTS")
    print(f"{'Total devices in Alexa:':<35} {len(alexa_devices):>8}")
    print(f"{'Currently exposed by HA:':<35} {len(ha_exposed):>8}")
    print(f"{'Orphaned devices:':<35} {len(orphans):>8}")

    # Save report
    save_report(alexa_devices, ha_exposed, orphans, exclude_count)

    # Show sample
    log("INFO", "Sample orphaned devices (first 10):")
    print()
    for entity_id in sorted(orphans)[:10]:
        friendly_name = alexa_devices.get(entity_id, "Unknown")
        print(f"  - {entity_id:<50} ({friendly_name})")
    if len(orphans) > 10:
        print(f"  ... and {len(orphans) - 10} more")
    print()

    # Cleanup options
    print_header("CLEANUP OPTIONS")
    print("  [1] Delete via Home Assistant (recommended)")
    print("  [2] Generate service call YAML")
    print("  [3] Nuclear option - delete ALL and rediscover")
    print("  [4] Cancel")
    print()

    if args.auto_delete:
        choice = "1"
    else:
        choice = input("Choose option (1-4): ").strip()

    if choice == "1":
        # Use Home Assistant integration
        token = load_oauth_token()
        if not token:
            log("ERROR", "Could not load OAuth token")
            log("INFO", "Make sure Home Assistant Alexa integration is configured")
            return

        if not args.auto_delete:
            confirm = input(f"\nDelete {len(orphans)} orphaned devices? (yes/no): ")
            if confirm.lower() != "yes":
                log("INFO", "Cancelled")
                return

        deleted, failed = send_delete_report(list(orphans), token)

        log("SUCCESS", f"All {deleted} devices submitted for deletion")
        if failed > 0:
            log("WARNING", f"{failed} deletions failed")

        log("INFO", "\nDevices should disappear from Alexa app in 1-2 minutes")

    elif choice == "2":
        # Generate YAML
        print("\n# Copy and paste into Developer Tools → Services")
        print("# Service: python_script.alexa_delete_devices\n")
        print("entity_ids:")
        for entity_id in sorted(orphans):
            print(f"  - {entity_id}")
        print()

    elif choice == "3":
        nuclear_option()

    else:
        log("INFO", "Cancelled")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except (
        requests.RequestException,
        json.JSONDecodeError,
        KeyError,
        OSError,
        ValueError,
    ) as e:
        log("ERROR", f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

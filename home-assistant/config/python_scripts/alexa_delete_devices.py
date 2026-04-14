"""
Alexa Device Deletion Python Script for Home Assistant

This script sends DeleteReport events to Alexa via Home Assistant's
built-in Alexa integration to remove devices from the Alexa Smart Home skill.

Usage in Home Assistant:
  Service: python_script.alexa_delete_devices
  Data:
    entity_ids:
      - light.old_device
      - sensor.removed_sensor

Author: Home Assistant Setup
Version: 1.0.0
"""

import logging

# Create a logger for this script (python_scripts environment may not provide a logger variable)
logger = logging.getLogger("python_script.alexa_delete_devices")

# Access hass from globals (python_scripts provides hass global)
hass = globals().get("hass")
if hass is None:
    logger.error(
        "hass object not available in globals(); this script must run "
        "inside the Home Assistant python_scripts environment"
    )
    # Provide a clear error result and avoid running the rest of the
    # script when hass is missing
    result = {
        "success": False,
        "error": "hass not available",
        "deleted": 0,
        "failed": 0,
    }
    # Do not use `return` at module level (invalid in a top-level script); the later
    # `if "result" not in locals():` guard will preserve this error result.

# Get entity_ids from service call data (ensure 'data' exists for static analysis)
data = globals().get("data", {})
entity_ids = data.get("entity_ids", [])

# Initialize counters and ALEXA_COMPONENT so result object can always reference them
DELETED_COUNT = 0
FAILED_COUNT = 0
ALEXA_COMPONENT = None

if not entity_ids:
    logger.error("No entity_ids provided to alexa_delete_devices")
else:
    # Get the Alexa integration
    if hass is None:
        logger.error("Cannot proceed: hass is not available")
    else:
        ALEXA_COMPONENT = hass.data.get("alexa")

    if not ALEXA_COMPONENT:
        logger.error("Alexa integration not found - is it configured?")
    else:
        # Send delete report for each entity
        DELETED_COUNT = 0
        FAILED_COUNT = 0

        for entity_id in entity_ids:
            try:
                # Local alias to satisfy static type checkers and ensure hass is not None
                hass_local = hass
                if hass_local is None:
                    raise RuntimeError("hass object is not available")
                # Use Home Assistant's built-in Alexa delete functionality
                # Use synchronous service call to avoid calling
                # hass.async_create_task on an Optional hass
                hass_local.services.call(
                    "alexa",
                    "delete_event",
                    {"entity_id": entity_id},
                    False,
                )
                DELETED_COUNT += 1
                logger.info("Queued DeleteReport for %s", entity_id)

            except (AttributeError, TypeError, RuntimeError, ValueError) as e:
                FAILED_COUNT += 1
                logger.error("Failed to delete %s: %s", entity_id, e)

        logger.info(
            "Alexa device deletion: %d queued, %d failed",
            DELETED_COUNT,
            FAILED_COUNT,
        )

# Return success (or preserve earlier error result)
if "result" not in locals():
    result = {
        "success": True,
        "deleted": DELETED_COUNT if "DELETED_COUNT" in locals() else 0,
        "failed": FAILED_COUNT if "FAILED_COUNT" in locals() else 0,
    }

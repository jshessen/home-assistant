#!/bin/bash
#
# Fix for Home Assistant Alexa OAuth TypeError Bug
# GitHub Issue: https://github.com/home-assistant/core/issues/155886
#
# This script patches the Alexa integration to fix a timezone comparison bug
# that prevents OAuth authentication from working in HA 2025.11.0+
#
# BUG: Line 113 in alexa/auth.py compares timezone-aware and timezone-naive datetimes
# FIX: Wraps preemptive_expire_time with dt_util.as_utc() for consistent comparison
#
# Usage: ./scripts/fix-alexa-oauth-bug.sh
#
# ⚠️  REAPPLY AFTER EVERY HA UPDATE — the patch lives inside the container image.
# Quick one-liner (patch + restart):
#   ./scripts/fix-alexa-oauth-bug.sh && docker restart home-assistant
#
# Check if already applied:
#   docker exec home-assistant grep -n "dt_util.as_utc(preemptive_expire_time)" \
#     /usr/src/homeassistant/homeassistant/components/alexa/auth.py
# See docs/alexa/README-ALEXA-FIX.md for full details.
#

set -e  # Exit on error

CONTAINER_NAME="home-assistant"
AUTH_FILE="/usr/src/homeassistant/homeassistant/components/alexa/auth.py"
BACKUP_FILE="${AUTH_FILE}.backup"

echo "=========================================="
echo "Home Assistant Alexa OAuth Bug Fix"
echo "GitHub Issue #155886"
echo "=========================================="
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ ERROR: Container '${CONTAINER_NAME}' is not running"
    echo "   Start Home Assistant first with: make hacs (or make all)"
    exit 1
fi

echo "✓ Container '${CONTAINER_NAME}' is running"

# Check if file exists
if ! docker exec "${CONTAINER_NAME}" test -f "${AUTH_FILE}"; then
    echo "❌ ERROR: File ${AUTH_FILE} not found in container"
    exit 1
fi

echo "✓ Found ${AUTH_FILE}"

# Check if already patched
if docker exec "${CONTAINER_NAME}" grep -q "dt_util.as_utc(preemptive_expire_time)" "${AUTH_FILE}"; then
    echo ""
    echo "✓ Fix is already applied!"
    echo ""
    echo "Current code:"
    docker exec "${CONTAINER_NAME}" sed -n '110,115p' "${AUTH_FILE}"
    echo ""
    echo "No action needed. Alexa OAuth should work correctly."
    exit 0
fi

echo "✓ Bug detected - fix needs to be applied"
echo ""

# Create backup if it doesn't exist
if ! docker exec "${CONTAINER_NAME}" test -f "${BACKUP_FILE}"; then
    echo "Creating backup: ${BACKUP_FILE}"
    docker exec "${CONTAINER_NAME}" cp "${AUTH_FILE}" "${BACKUP_FILE}"
    echo "✓ Backup created"
else
    echo "✓ Backup already exists"
fi

# Apply the fix
echo ""
echo "Applying fix..."
docker exec "${CONTAINER_NAME}" sed -i \
    's/return dt_util\.utcnow() < preemptive_expire_time/return dt_util.utcnow() < dt_util.as_utc(preemptive_expire_time)/' \
    "${AUTH_FILE}"

# Verify the fix was applied
if docker exec "${CONTAINER_NAME}" grep -q "dt_util.as_utc(preemptive_expire_time)" "${AUTH_FILE}"; then
    echo "✓ Fix applied successfully"
    echo ""
    echo "Patched code:"
    docker exec "${CONTAINER_NAME}" sed -n '110,115p' "${AUTH_FILE}"
    echo ""
    echo "=========================================="
    echo "✓ PATCH COMPLETE"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Restart Home Assistant: docker restart ${CONTAINER_NAME}"
    echo "  2. Wait for Home Assistant to start (~30 seconds)"
    echo "  3. Try linking your Alexa skill again"
    echo ""
    echo "If you need to restore the original file:"
    echo "  docker exec ${CONTAINER_NAME} cp ${BACKUP_FILE} ${AUTH_FILE}"
    echo "  docker restart ${CONTAINER_NAME}"
    echo ""
else
    echo "❌ ERROR: Fix was not applied correctly"
    echo "   Please check manually or report this issue"
    exit 1
fi

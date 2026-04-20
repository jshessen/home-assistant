---
mode: "agent"
tools: ["read_file"]
description: "Analyze battery dashboard configuration and suggest improvements"
---

Analyze the battery dashboard configuration and produce a coverage and maintenance report.

## Step 1: Read the dashboard

Read the file: `home-assistant/config/lovelace/battery_dashboard.yaml`

## Step 2: Analyze for the following gaps

For each device/entity listed in the dashboard, check:

1. **Missing Battery Notes `note`** — Devices that have no brand/model annotation. These can't be used for predictive lifespan estimates.
2. **Missing `battery_last_replaced` tracking** — Devices with no replacement date logged. Without this, battery lifespan data cannot accumulate.
3. **Critical level (below 20%)** — Devices that need immediate battery replacement.
4. **Warning level (20–40%)** — Devices approaching replacement threshold.

## Step 3: Produce a structured report

Output the following sections:

### Coverage Summary

- Total devices in dashboard
- Devices with Battery Notes (brand/model): X / Total
- Devices with replacement date tracked: X / Total
- Devices critical (<20%): X
- Devices warning (20–40%): X

### Devices Needing Battery Notes Entry

List each device missing a note, sorted by battery level (lowest first).

### Devices Needing Replacement Logging

List each device with no `battery_last_replaced` entity or value.

### Replacement Priority

Rank devices by urgency:

1. Critical (<20%) with no replacement history — replace immediately
2. Warning (20–40%) with no replacement history — replace soon
3. Critical (<20%) with replacement history — replace based on normal cycle
4. Warning (20–40%) with replacement history — monitor

## Step 4: Suggestions

Recommend which 3–5 devices should be prioritized for Battery Notes data entry to maximize coverage of high-traffic or hard-to-access devices.

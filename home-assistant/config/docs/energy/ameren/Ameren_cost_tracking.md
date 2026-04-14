# Energy Cost Tracking Setup

## Overview

This guide explains how to set up electricity cost tracking in Home Assistant using the `utility_meter` integration combined with seasonal template sensors. The setup automatically calculates your monthly and daily electricity costs based on Ameren Missouri's seasonal rate structure.

## ⚡ NEW: Automated Rate Management

**A Python script now automates rate tracking!**

- 📥 **Auto-downloads** PDFs from Ameren Missouri
- 📊 **Parses seasonal rates** (Summer flat, Winter tiered)
- 🔄 **Monthly automation** checks for rate updates
- 📈 **Smart templates** auto-switch by season

**See:** [Ameren_QUICK_REFERENCE.md](Ameren_QUICK_REFERENCE.md) for the full automated system.

## Quick Start

### 1. **Update Rate Values**

After restarting Home Assistant, you'll have two new helper entities:

- **`input_number.ameren_mo_kwh_rate`** - Your per-kWh rate (default: $0.1264)
- **`input_number.ameren_mo_monthly_fixed`** - Monthly service charge (default: $9.00)

**To update rates without editing YAML:**

1. Go to **Settings → Devices & Services → Helpers**
2. Search for "Ameren MO"
3. Click each helper and update the value
4. Rates update instantly - no restart required!

### 2. **Verify Your Energy Source Sensor**

The default configuration uses `sensor.drier_energy` as the consumption source. You need to update this to match your actual utility meter sensor.

**Find your sensor:**

1. Go to **Developer Tools → States**
2. Search for energy-related sensors (look for units: kWh)
3. Common patterns:
   - `sensor.smart_meter_energy`
   - `sensor.utility_meter_energy`
   - `sensor.total_kwh`
   - Smart plug/strip energy readings from Z-Wave

**Once identified, update these files:**

- [utility_meter.yaml](../../utility_meter.yaml) - Replace `sensor.drier_energy` with your sensor
- [energy_costs.yaml](../../templates/energy_costs.yaml) - Replace `sensor.drier_energy` in template sensor definitions

### 3. **New Sensors Created**

After configuration and restart, these sensors will be available:

| Sensor | Purpose | Updates |
| -------- | --------- | --------- |
| `sensor.monthly_electricity` | Total kWh consumed this month | Monthly reset |
| `sensor.daily_electricity` | Total kWh consumed today | Daily reset (midnight) |
| `sensor.monthly_electricity_cost` | Calculated monthly cost | Real-time |
| `sensor.daily_electricity_cost` | Daily consumption × rate | Real-time |
| `sensor.estimated_remaining_monthly_cost` | Projected month-end cost | Real-time |

## How It Works

### Utility Meter

The `utility_meter` integration:

1. **Tracks cumulative consumption** - Monitors your energy meter's ever-increasing value
2. **Calculates deltas** - Subtracts previous period's total to get consumption
3. **Resets on schedule** - Automatically resets when the cycle completes (monthly/daily)

Example:

- Jan 1: Meter reads 1000 kWh (monthly reset happens)
- Jan 31: Meter reads 1042 kWh
- January consumption = 42 kWh

### Cost Calculation

Template sensors multiply consumption by rate:

```text
Monthly Cost = (Monthly Consumption × Rate per kWh) + Fixed Charge
            = (42 kWh × $0.1264) + $9.00
            = $5.31 + $9.00
            = $14.31
```

The calculation happens in [energy_costs.yaml](../../templates/energy_costs.yaml) using Jinja2 templating.

## Ameren Missouri Rates

**Actual Rate Structure (Effective June 1, 2025):**

### Summer (June - September)

- **Fixed Monthly Charge:** $9.00
- **Low-Income Pilot Charge:** $0.19
- **Energy Rate:** $0.1560/kWh (15.60¢) - **Flat rate**

### Winter (October - May)

- **Fixed Monthly Charge:** $9.00
- **Low-Income Pilot Charge:** $0.19
- **Energy Rate:** **Tiered pricing**
  - First 750 kWh: $0.1062/kWh (10.62¢)
  - Over 750 kWh: $0.0714/kWh (7.14¢)

### Rate Management

**Automated System:** [`packages/ameren/ameren_rate_manager.py`](../../packages/ameren/ameren_rate_manager.py)

- Downloads PDFs from [Ameren Rates](https://www.ameren.com/missouri/residential/rates-tariffs)
- Parses Rate 1(M) tariff sheets
- Auto-updates seasonal helpers monthly

**Manual Updates:**

1. Log into [Ameren Account](https://www.ameren.com)
2. Check your latest bill for "Rate 1M (Residential)"
3. Update helpers in Settings → Devices & Services → Helpers

## Configuration Files

### [utility_meter.yaml](../../utility_meter.yaml)

Defines consumption tracking meters:

```yaml
monthly_electricity:
  source: sensor.drier_energy    # YOUR ENERGY METER HERE
  cycle: monthly
  name: Monthly Electricity
```

**Key settings:**

- `source` - Must point to a sensor with cumulative kWh values
- `cycle` - Reset frequency (daily, monthly, quarterly, yearly)
- `unit_prefix: k` - Converts Wh input to kWh output

### [input_number.yaml](../../input_number.yaml)

Defines adjustable rate input helpers:

```yaml
ameren_mo_kwh_rate:
  initial: 0.1264
  min: 0.05
  max: 0.25
  step: 0.0001
```

Users can adjust these in the UI without editing YAML.

### [energy_costs.yaml](../../templates/energy_costs.yaml)

Calculates costs using template sensors:

```jinja2
{% set consumption = states('sensor.monthly_electricity') | float(0) %}
{% set rate = states('input_number.ameren_mo_kwh_rate') | float(0.1264) %}
{% set fixed_charge = states('input_number.ameren_mo_monthly_fixed') | float(9.00) %}
{{ (consumption * rate + fixed_charge) | round(2) }}
```

## Advanced: Time-of-Use Rates

Ameren Missouri offers **time-of-use** plans where peak and off-peak hours have different rates:

- **Peak Hours:** 9 AM - 9 PM → $0.15/kWh
- **Off-Peak Hours:** 9 PM - 9 AM → $0.10/kWh

### Implementation (Optional)

1. **Uncomment rate inputs** in [input_number.yaml](../../input_number.yaml):

```yaml
ameren_mo_peak_rate:
  initial: 0.1500
  # ...

ameren_mo_offpeak_rate:
  initial: 0.1000
  # ...
```

1. **Create separate metering** in [utility_meter.yaml](../../utility_meter.yaml):

```yaml
daily_electricity_peak:
  source: sensor.daily_electricity
  cycle: daily
  tariffs:
    - peak
    - offpeak

daily_electricity_offpeak:
  source: sensor.daily_electricity
  cycle: daily
  tariffs:
    - peak
    - offpeak
```

1. **Add automation** to switch tariff at peak/off-peak times:

```yaml
automation:
  - trigger: time
    at: "09:00:00"
    action:
      service: select.select_option
      target:
        entity_id: select.daily_electricity_peak
      data:
        option: "peak"

  - trigger: time
    at: "21:00:00"
    action:
      service: select.select_option
      target:
        entity_id: select.daily_electricity_peak
      data:
        option: "offpeak"
```

1. **Update cost templates** to account for separate tariffs

See [HA utility_meter documentation](https://www.home-assistant.io/integrations/utility_meter/) for complete TOU examples.

## Adding Water & Gas Tracking

The same pattern extends to water and gas:

### 1. Create separate utility meters

Add to [utility_meter.yaml](../../utility_meter.yaml):

```yaml
monthly_water:
  source: sensor.water_meter_consumption  # Your water meter
  cycle: monthly
  unit_of_measurement: "gal"

monthly_gas:
  source: sensor.gas_meter_consumption    # Your gas meter
  cycle: monthly
  unit_of_measurement: "therm"
```

### 2. Create input helpers for rates

Add to [input_number.yaml](../../input_number.yaml):

```yaml
ameren_mo_water_rate:
  name: "Water Rate"
  unit_of_measurement: "$/gal"
  initial: 0.00456  # Example: $4.56 per 1000 gallons

ameren_mo_gas_rate:
  name: "Gas Rate"
  unit_of_measurement: "$/therm"
  initial: 0.8500
```

### 3. Create cost templates

Add to [energy_costs.yaml](energy_costs.yaml):

```jinja2
sensor:
  - name: "Monthly Water Cost"
    state: >-
      {% set consumption = states('sensor.monthly_water') | float(0) %}
      {% set rate = states('input_number.ameren_mo_water_rate') | float(0) %}
      {{ (consumption * rate) | round(2) }}

  - name: "Monthly Gas Cost"
    state: >-
      {% set consumption = states('sensor.monthly_gas') | float(0) %}
      {% set rate = states('input_number.ameren_mo_gas_rate') | float(0) %}
      {{ (consumption * rate) | round(2) }}
```

## Troubleshooting

### Cost sensors show 0.00 or unknown

**Cause:** The source sensor is unavailable or doesn't exist

**Fix:**

1. Check **Developer Tools → States** - verify source sensor exists
2. Ensure utility_meter's source points to the correct sensor
3. Restart Home Assistant if you edited configuration files

### Monthly reset doesn't happen on expected day

**Cause:** Cycle timing issue or local timezone

**Fix:**

Update [utility_meter.yaml](../utility_meter.yaml) to use cron for custom reset times:

```yaml
monthly_electricity:
  source: sensor.drier_energy
  cron: "0 17 L * *"  # Reset at 5 PM on last day of month
```

(Requires Home Assistant restart)

### Rates not updating

**Cause:** Helper entity not recognized in template

**Fix:**

1. Verify `input_number.ameren_mo_kwh_rate` exists in **Settings → Devices & Services → Helpers**
2. Check template YAML syntax in [energy_costs.yaml](energy_costs.yaml)
3. Check logs: **Settings → System → Logs** for template errors

## Dashboard Integration

Add to your Lovelace dashboard to visualize costs:

```yaml
type: entities
title: Energy Costs
entities:
  - entity: sensor.monthly_electricity_cost
  - entity: sensor.daily_electricity_cost
  - entity: sensor.estimated_remaining_monthly_cost
  - entity: input_number.ameren_mo_kwh_rate
  - entity: input_number.ameren_mo_monthly_fixed
```

Or create a custom **History Statistics** card to graph costs over time:

```yaml
type: custom:auto-entities
filter:
  template: "{{ state_attr('sensor.monthly_electricity', 'unit_of_measurement') }}"
sort:
  method: name
```

## References

- [Home Assistant Utility Meter Integration](https://www.home-assistant.io/integrations/utility_meter/)
- [Ameren Missouri Rates & Tariffs](https://www.ameren.com/missouri/residential/rates-tariffs)
- [Home Assistant Template Sensors](https://www.home-assistant.io/integrations/template/)
- [YAML Mode in Home Assistant](https://www.home-assistant.io/docs/configuration/)

## Next Steps

1. ✅ Verify your energy meter sensor exists
2. ✅ Update [utility_meter.yaml](../utility_meter.yaml) with correct source
3. ✅ Update rate values via UI helpers
4. 🔄 Restart Home Assistant
5. ✅ Check **Developer Tools → States** for new sensors
6. ✅ Add to dashboard and monitor costs!

---

**Questions or issues?** Check the [Home Assistant Community Forum](https://community.home-assistant.io/) or visit the [official documentation](https://www.home-assistant.io/).

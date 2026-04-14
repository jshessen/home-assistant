# Energy Cost Tracking - Quick Start Guide

## ✅ Configuration Complete

Your Home Assistant is now configured with:

- **Utility Meter** - Tracks daily and monthly consumption
- **Rate Helpers** - Adjustable Ameren MO rates (UI-editable)
- **Cost Templates** - Automatic cost calculations
- **Documentation** - Complete setup and reference guide

## 📋 Next Steps (Required)

### 1. Identify Your Energy Meter Sensor

Go to **Developer Tools → States** and find your electricity meter:

**Look for sensors with these patterns:**

- `sensor.*energy*` (kWh units)
- `sensor.*kwh*`
- `sensor.smart_meter*`
- Z-Wave/Zigbee energy readings: `sensor.switch_energy`, `sensor.plug_energy`, etc.

From your setup, you likely have:

- `sensor.drier_energy` - Dryer smart plug
- `sensor.washer_energy` - Washer smart plug
- Or a main utility meter sensor

**Which sensor should you use?**

- Use your **main utility meter** if available (reports total household consumption)
- Otherwise, sum multiple smart plug readings (see Advanced section in docs)

### 2. Update Configuration

Edit [`utility_meter.yaml`](../../utility_meter.yaml) - Replace `sensor.drier_energy` with your actual meter:

```yaml
monthly_electricity:
  source: sensor.your_actual_meter_here  # ← CHANGE THIS
  name: Monthly Electricity
  cycle: monthly
```

### 3. Update Rate (Optional - Default Works for Ameren MO)

The rates are already set to Ameren MO defaults:

- **Rate:** $0.1264/kWh
- **Fixed:** $9.00/month

**To update without editing files:**

1. Go to **Settings → Devices & Services → Helpers**
2. Search: "Ameren MO"
3. Click each and adjust to your actual rates
4. Changes apply instantly!

**To find your actual rates:**

1. Log into your Ameren account: <https://www.ameren.com>
2. View your latest bill for "Rate 1M (Residential)"
3. Enter rate in `input_number.ameren_mo_kwh_rate`

### 4. Restart Home Assistant

After changing the source sensor, restart:

**Option A:** Settings → System → Restart Home Assistant

**Option B:** Terminal

```bash
docker restart home-assistant
```

### 5. Verify Sensors Are Working

Wait 2 minutes after restart, then check **Developer Tools → States**:

- `sensor.monthly_electricity` - Shows kWh consumed
- `sensor.daily_electricity` - Shows today's kWh
- `sensor.monthly_electricity_cost` - Shows $$ cost
- `sensor.daily_electricity_cost` - Shows today's cost
- `input_number.ameren_mo_kwh_rate` - Your rate (editable)
- `input_number.ameren_mo_monthly_fixed` - Fixed charge (editable)

If sensors show `unavailable` or `0`:

- The source sensor doesn't exist or has no value yet
- Double-check the sensor name and restart HA again

## 📊 Add to Dashboard

Add a card to your Lovelace dashboard:

```yaml
type: entities
title: Energy Costs
entities:
  - entity: sensor.monthly_electricity_cost
    name: "This Month: "
  - entity: sensor.daily_electricity_cost
    name: "Today: "
  - entity: sensor.estimated_remaining_monthly_cost
    name: "Projected Month Total: "
  - entity: input_number.ameren_mo_kwh_rate
    name: "Your Rate ($/kWh): "
```

## 📚 Full Documentation

See [Ameren_cost_tracking.md](Ameren_cost_tracking.md) for:

- **Troubleshooting** - Fix common issues
- **Advanced Configuration** - Time-of-use rates, water/gas tracking
- **How It Works** - Detailed explanation of calculation logic
- **Dashboard Examples** - History graphs and custom cards

## 🆘 Troubleshooting

### "Sensors show unavailable"

**Fix:**

```bash
# Check sensor exists:
docker exec home-assistant /bin/bash -c \
  "echo -e 'states:' && python3 -c \"import json; print(json.dumps([s for s in [SENSOR] if 'energy' in s.lower()], indent=2))\" "
```

Then verify the sensor name is correct and restart.

### "Cost shows 0.00"

**Causes:**

1. Source sensor has no data yet (new meter)
2. Meter hasn't updated since configuration
3. Sensor name doesn't match

**Fix:**

- Wait 24 hours for first billing cycle
- Verify source sensor is reporting values
- Check logs: Settings → System → Logs

### Rates not updating when I change input_number

**Fix:**

1. Make sure you're editing the right helper (Home Assistant → Settings → Helpers)
2. Check that your template sensors reference the correct `input_number` entity
3. Restart Templates in Developer Tools if needed

## 📞 Need Help?

**Refer to:**

- [Complete Energy Tracking Guide](Ameren_cost_tracking.md)
- [Home Assistant Utility Meter Docs](https://www.home-assistant.io/integrations/utility_meter/)
- [HA Community Forum](https://community.home-assistant.io/) for similar setups

---

**Configuration files created:**

- ✅ `utility_meter.yaml` - Meter tracking
- ✅ `input_number.yaml` - Rate helpers
- ✅ `templates/energy_costs.yaml` - Cost calculations
- ✅ `docs/energy/ameren/Ameren_cost_tracking.md` - Full documentation

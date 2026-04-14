# Ameren Rate Manager - Quick Reference

## ⚡ One-Time Setup Complete

Your system is now configured with:

- ✅ Seasonal rate awareness (Summer/Winter)
- ✅ Tiered winter pricing (750 kWh breakpoint)
- ✅ Automated PDF downloading capability
- ✅ Smart cost templates that auto-switch by season

## 🎯 Current Configuration (February 2026 - Winter Season)

### Active Rates

- **Fixed Monthly:** $9.19 (Customer $9.00 + Low-Income Pilot $0.19)
- **Winter Tier 1:** $0.1062/kWh (first 750 kWh)
- **Winter Tier 2:** $0.0714/kWh (over 750 kWh)

### Example Bills (Winter)

| Consumption | Total Cost | Effective Rate |
|-------------|------------|----------------|
| 500 kWh     | $62.29     | $0.1062/kWh    |
| 750 kWh     | $88.84     | $0.1062/kWh    |
| 1000 kWh    | $106.69    | $0.0975/kWh    |
| 1500 kWh    | $142.39    | $0.0888/kWh    |

## 📊 New Sensors Available

### Rate Information

- `sensor.current_electricity_season` - "Winter" or "Summer"
- `sensor.current_electricity_rate` - Effective $/kWh (auto-calculated)

### Costs

- `sensor.monthly_electricity_cost` - Total bill with seasonal logic
- `sensor.daily_electricity_cost` - Today's cost
- `sensor.estimated_monthly_bill_projection` - Projected month-end total

### Helpers (UI Editable)

- `input_number.ameren_mo_monthly_fixed` - Fixed charges ($9.19)
- `input_number.ameren_mo_summer_rate` - Summer rate ($0.1560/kWh)
- `input_number.ameren_mo_winter_tier1_rate` - Winter tier 1 ($0.1062/kWh)
- `input_number.ameren_mo_winter_tier2_rate` - Winter tier 2 ($0.0714/kWh)
- `input_number.ameren_mo_winter_tier1_limit` - Tier breakpoint (750 kWh)

## 🔧 Manual Rate Updates

### Option 1: Use Python Script (Recommended)

```bash
# Check current rates from cached PDFs
cd /opt/docker/home-assistant/home-assistant/config/packages/ameren
python3 ameren_rate_manager.py --check

# Download latest PDFs from Ameren
python3 ameren_rate_manager.py --download --parse --check

# See what would be updated (dry run)
python3 ameren_rate_manager.py --update --dry-run
```

### Option 2: Update via Home Assistant UI

1. **Settings → Devices & Services → Helpers**
2. Search: "Ameren MO"
3. Click each helper and edit values
4. Changes apply instantly!

## 🤖 Automatic Updates

A monthly automation is configured:

- **Trigger:** 1st of each month at 3 AM
- **Action:** Downloads latest PDFs and logs changes
- **Service:** `shell_command.update_ameren_rates`

To manually trigger:

```yaml
service: shell_command.update_ameren_rates
```

## 🔄 Season Switch Behavior

The system automatically switches rates based on calendar month:

### Summer Mode (June 1 - September 30)

- Flat rate applies to all consumption
- `sensor.monthly_electricity_cost` = (kWh × Summer Rate) + Fixed

### Winter Mode (October 1 - May 31)

- Tiered rate applies:
  - First 750 kWh at Tier 1 rate
  - Remaining kWh at Tier 2 rate
- `sensor.monthly_electricity_cost` = (Tier1 Cost + Tier2 Cost) + Fixed

**No manual intervention needed** - templates handle the switch automatically!

## 📝 TODO: Update Energy Source

The configuration currently uses `sensor.drier_energy` as a placeholder.

**Update to your actual utility meter:**

1. Find your meter: **Developer Tools → States** → Search "energy" or "kwh"
2. Edit [`utility_meter.yaml`](../../utility_meter.yaml):

   ```yaml
   monthly_electricity:
     source: sensor.your_actual_meter  # ← CHANGE THIS
   ```

3. Restart Home Assistant

## 📚 Full Documentation

- **[Complete Guide](Ameren_cost_tracking.md)** - Detailed setup, troubleshooting, TOU rates
- **[Ameren Package README](Ameren_PACKAGE_README.md)** - Script usage, automation details
- **[Quick Start](Ameren_QUICK_START.md)** - Basic setup steps

## 🆘 Troubleshooting

### Rate Manager Script

```bash
# If script errors occur, check Python availability
python3 --version  # Should show Python 3.x

# Verify pdftotext is installed
which pdftotext  # Should show /usr/bin/pdftotext

# Check cached rates
cat packages/ameren/parsed_rates.json
```

### Template Sensors Not Working

1. **Check sensor names:**
   - Developer Tools → States
   - Search: "electricity"

2. **Reload templates:**
   - Developer Tools → YAML
   - Click "Template Entities" → Reload

3. **Check logs:**
   - Settings → System → Logs
   - Search: "template" or "energy_costs"

### Costs Show $0.00

- Energy meter hasn't been configured yet (see TODO above)
- Utility meter source sensor doesn't exist
- Wait 24 hours for first billing cycle to accumulate data

## 🎓 Understanding Tiered Winter Rates

**Example:** 1000 kWh consumption in February

```text
Tier 1 Cost = 750 kWh × $0.1062 = $79.65
Tier 2 Cost = 250 kWh × $0.0714 = $17.85
Energy Cost = $79.65 + $17.85 = $97.50
Total Bill  = $97.50 + $9.19 = $106.69

Effective Rate = $106.69 ÷ 1000 kWh = $0.1067/kWh
```

The `sensor.current_electricity_rate` calculates this effective blended rate automatically!

## 🔮 Next Steps

1. ✅ **Verify sensors work** - Check Developer Tools → States
2. ✅ **Add to dashboard** - Create energy cost card
3. ⏳ **Update energy source** - Point to real utility meter
4. ⏳ **Monitor first billing cycle** - Verify costs match actual bill
5. ⏳ **Set up notifications** - Alert when bills exceed threshold

---

**Script Location:** `/config/packages/ameren/ameren_rate_manager.py`
**Cached PDFs:** `/config/packages/ameren/*.pdf`
**Parsed Data:** `/config/packages/ameren/parsed_rates.json`

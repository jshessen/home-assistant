# Ameren Missouri Rate Management Package

This package automates electricity rate tracking for Ameren Missouri residential customers.

## What's Included

### 📄 Files

- **`ameren_rate_manager.py`** - Python script to download, parse, and manage rates
- **`packages/ameren.yaml`** - Home Assistant automation + shell_command package
- **`UECSheet54Rate1MRES.pdf`** - Residential Rate 1(M) tariff (cached)
- **`UECSheet63MiscChgs.pdf`** - Miscellaneous charges (cached)
- **`UECSheet53TOCRates.pdf`** - Rate table of contents (cached)
- **`parsed_rates.json`** - Extracted rate data (auto-generated)

### ⚙️ Features

1. **Automatic PDF Downloads** - Fetches latest rate sheets from Ameren
2. **Smart Parsing** - Extracts rates using regex patterns
3. **Seasonal Awareness** - Handles Summer (flat) vs Winter (tiered) rates
4. **Cost Calculation** - Computes bills based on consumption and season
5. **HA Integration** - Updates `input_number` helpers automatically
6. **Historical Tracking** - Caches rates and tracks changes

## Current Rates (Effective June 1, 2025)

### Summer Rates (June - September)

- **Customer Charge:** $9.00/month
- **Low-Income Charge:** $0.19/month
- **Energy Rate:** $0.1560/kWh (15.60¢)

### Winter Rates (October - May)

- **Customer Charge:** $9.00/month
- **Low-Income Charge:** $0.19/month
- **Energy Rate (Tiered):**
  - First 750 kWh: $0.1062/kWh (10.62¢)
  - Over 750 kWh: $0.0714/kWh (7.14¢)

## Usage

### Command Line

```bash
# Check current rates
python3 ameren_rate_manager.py --check

# Download latest PDFs
python3 ameren_rate_manager.py --download

# Parse PDFs and update cache
python3 ameren_rate_manager.py --parse

# Show what would be updated (dry run)
python3 ameren_rate_manager.py --update --dry-run

# Update Home Assistant helpers
python3 ameren_rate_manager.py --update
```

### Home Assistant Service Calls

```yaml
# Manually trigger rate update
service: shell_command.update_ameren_rates
```

### Automation

The package includes an automation (in `packages/ameren.yaml`) that:

- Runs on the 1st of each month at 3 AM
- Downloads latest PDFs from Ameren
- Parses rates and logs changes
- (Manual HA update required for now)

## Home Assistant Helpers

The following `input_number` helpers are created in [`../../input_number.yaml`](../../input_number.yaml):

- `input_number.ameren_mo_monthly_fixed` - Fixed monthly charges ($9.19)
- `input_number.ameren_mo_summer_rate` - Summer flat rate ($0.1560/kWh)
- `input_number.ameren_mo_winter_tier1_rate` - Winter rate for first 750 kWh ($0.1062/kWh)
- `input_number.ameren_mo_winter_tier2_rate` - Winter rate over 750 kWh ($0.0714/kWh)
- `input_number.ameren_mo_winter_tier1_limit` - Winter tier breakpoint (750 kWh)

## Template Sensors

The following sensors are created in [`../../templates/energy_costs.yaml`](../../templates/energy_costs.yaml):

- `sensor.current_electricity_season` - Current billing season (Summer/Winter)
- `sensor.current_electricity_rate` - Effective $/kWh rate for current consumption
- `sensor.monthly_electricity_cost` - Total monthly bill with seasonal logic
- `sensor.daily_electricity_cost` - Today's consumption cost
- `sensor.estimated_monthly_bill_projection` - Projected month-end total

## How It Works

### 1. PDF Download

```python
# Downloads from Ameren URLs and caches locally
urlretrieve(
    'https://www.ameren.com/-/media/rates/missouri/residential/electric-rates/rates/uecsheet54rate1mres.ashx',
    'UECSheet54Rate1MRES.pdf'
)
```

### 2. Text Extraction

```bash
# Uses pdftotext with layout preservation
pdftotext -layout UECSheet54Rate1MRES.pdf output.txt
```

### 3. Rate Parsing

```python
# Regex patterns extract structured data
summer_section = re.search(
    r'Summer Rate.*?Customer Charge.*?\$(\d+\.\d{2}).*?'
    r'Energy Charge.*?(\d+\.\d{2})¢',
    text, re.DOTALL
)
```

### 4. Seasonal Logic

```python
# Template sensors auto-switch based on month
{% set month = now().month %}
{% if 6 <= month <= 9 %}
  Summer
{% else %}
  Winter
{% endif %}
```

### 5. Tiered Calculation (Winter)

```python
# Calculates blended rate for mixed-tier usage
if consumption <= 750:
    cost = consumption * 0.1062
else:
    cost = (750 * 0.1062) + ((consumption - 750) * 0.0714)
```

## Dependencies

### System Tools

- `pdftotext` (from `poppler-utils`) - ✅ Installed
- `python3` - ✅ Available in HA container

### Python Libraries (Optional)

- `requests` - For HA REST API updates (fallback: manual)

## Troubleshooting

### "pdftotext not found"

```bash
# Install poppler-utils (already installed on your system)
apt-get install poppler-utils
```

### "Failed to download PDF"

- Check internet connectivity
- Verify Ameren URLs haven't changed
- Use cached PDFs: Skip `--download` flag

### "No rates loaded"

```bash
# Re-parse from cached PDFs
python3 ameren_rate_manager.py --parse --check
```

### Rates not updating in HA

```bash
# Check current values
python3 ameren_rate_manager.py --update --dry-run

# Manual update in HA:
# Settings → Devices & Services → Helpers → Edit values
```

## Extending to Other Utilities

The rate manager can be adapted for other utility providers:

1. **Update URLs** - Change `AMEREN_URLS` to your provider
2. **Modify Regex** - Adjust parsing patterns in `parse_residential_rates()`
3. **Season Logic** - Update `get_current_season()` if needed
4. **Rename Variables** - Change `ameren_mo_*` to match your provider

## Future Enhancements

- [ ] Support for time-of-use (TOU) plans
- [ ] Historical rate tracking and visualization
- [ ] Bill prediction accuracy scoring
- [ ] Notification when rates change
- [ ] Multi-provider support (gas, water)
- [ ] Auto-update HA helpers (currently dry-run only)

## References

- [Ameren MO Rates & Tariffs](https://www.ameren.com/missouri/residential/rates-tariffs)
- [Rate 1(M) PDF](https://www.ameren.com/-/media/rates/missouri/residential/electric-rates/rates/uecsheet54rate1mres.ashx)
- [Home Assistant Utility Meter](https://www.home-assistant.io/integrations/utility_meter/)
- [Home Assistant Template Sensors](https://www.home-assistant.io/integrations/template/)

## Support

For issues or questions:

1. Check [Ameren_cost_tracking.md](Ameren_cost_tracking.md)
2. Review logs: `python3 ameren_rate_manager.py --check`
3. Validate PDFs exist: `ls -lh packages/ameren/*.pdf`
4. Test parsing: `python3 ameren_rate_manager.py --parse`

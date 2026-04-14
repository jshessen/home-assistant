# Python 3.13 Quick Reference

## Version Check

```bash
python3.13 --version    # 3.13.2
python3 --version       # 3.11.2 (system)
```

## Virtual Environment Creation

```bash
# Create venv with Python 3.13
python3.13 -m venv /path/to/venv

# Activate
source /path/to/venv/bin/activate

# Install packages
python -m pip install package-name
```

## VS Code

- Default interpreter: `/usr/bin/python3.13`
- Reload window after Python changes: `Ctrl+Shift+P` → "Developer: Reload Window"

## Common Locations

- **Installation script**: `/opt/docker/home-assistant/scripts/install-python313.sh`
- **Full documentation**: `/opt/docker/home-assistant/home-assistant/config/docs/setup/PYTHON_313_SETUP.md`
- **Repository config**: `/etc/apt/sources.list.d/pascalroeleven.sources`

## Updates

```bash
sudo apt update
sudo apt upgrade python3.13
```

## Home Assistant Core

```bash
# Install HA in venv
python3.13 -m venv ~/homeassistant
source ~/homeassistant/bin/activate
pip install homeassistant
hass --version
```

---
**Quick tip**: Both Python 3.11 and 3.13 coexist. System uses 3.11, development uses 3.13.

# Python 3.13 Setup for Home Assistant Development

## Overview

This workspace uses **Python 3.13** from the community-maintained Debian 12 Bookworm backport repository. This ensures compatibility with the latest Home Assistant Core releases while maintaining a stable Debian 12 base system.

## Installation

Python 3.13 has been installed using the automated script:

```bash
/opt/docker/home-assistant/scripts/install-python313.sh
```

This script:
1. Adds the trusted PGP key from pascalroeleven.nl
2. Configures the Python 3.13 backport repository
3. Installs Python 3.13 alongside the system Python 3.11
4. Includes `python3.13-venv` (with pip) and `python3.13-dev`

**Source**: [Python 3.13 backport for Debian 12 bookworm](https://community.home-assistant.io/t/python-3-13-backport-for-debian-12-bookworm/842333)

## Installed Versions

- **System Python**: Python 3.11.2 at `/usr/bin/python3` (Debian default)
- **Development Python**: Python 3.13.2 at `/usr/bin/python3.13` (Backport)

Both versions coexist without conflict. The system continues to use Python 3.11 for Debian packages, while development work uses Python 3.13.

## VS Code Configuration

The workspace is configured to use Python 3.13 by default:

```json
"python.defaultInterpreterPath": "/usr/bin/python3.13"
```

This applies to all workspace folders:
- Home Assistant Config
- External Connectors
- Cloudflare Workers
- Root

## Creating Virtual Environments

### For Home Assistant Core (Python 3.13)

```bash
# Create new venv with Python 3.13
python3.13 -m venv /path/to/venv

# Activate
source /path/to/venv/bin/activate

# Upgrade pip (included in python3.13-venv)
pip install --upgrade pip

# Install Home Assistant
pip install homeassistant
```

### For Custom Components (Python 3.13)

```bash
# Keymaster custom component example
cd /opt/docker/home-assistant/keymaster-github
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_test.txt
```

## Docker Container Considerations

The **Home Assistant Docker container** runs its own Python environment and is **not affected** by the host Python installation. The Python 3.13 installation is for:

1. **Local development** - Testing custom components outside containers
2. **Script development** - Python scripts in `config/python_scripts/`
3. **Custom integrations** - Developing/testing custom_components
4. **External connectors** - Python services outside Docker

## Package Management

### Important Notes

- **No `python3.13-pip` package** - pip is included in `python3.13-venv`
- **Always use virtual environments** - Don't install packages globally
- **Use `python3.13 -m pip`** - Instead of calling `pip` directly

### Installing Dependencies

```bash
# In a virtual environment
source venv/bin/activate
python -m pip install package-name

# Or explicitly with python3.13
python3.13 -m pip install package-name
```

## Repository Details

- **Repository URL**: `http://deb.pascalroeleven.nl/python3.13`
- **Suite**: `bookworm-backports`
- **Architectures**: amd64, arm64, armhf
- **Signed by**: `/etc/apt/keyrings/deb-pascalroeleven.gpg`
- **Source**: [GitHub - pascallj/python3.13-backport](https://github.com/pascallj/python3.13-backport)

## Maintenance

### Updating Python 3.13

The backport repository receives updates automatically:

```bash
sudo apt update
sudo apt upgrade python3.13
```

### Checking for Updates

```bash
apt list --upgradable | grep python3.13
```

### Removing Python 3.13 (if needed)

```bash
sudo apt remove python3.13 python3.13-venv python3.13-dev
sudo apt autoremove
```

This will **not affect** your system Python 3.11.

## Home Assistant Compatibility

| HA Version | Minimum Python | Status |
|------------|----------------|--------|
| 2025.2+    | 3.13           | ✅ Compatible |
| 2024.x     | 3.12           | ⚠️ 3.13 works but not required |
| 2023.x     | 3.11           | ⚠️ 3.13 works but not required |

Home Assistant 2025.2 (released February 2025) requires Python 3.13. The backport ensures you can run the latest versions without upgrading from Debian 12.

## Troubleshooting

### Import Errors in VS Code

If you see import errors for `homeassistant.*`:

1. Verify interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose `/usr/bin/python3.13`
3. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Virtual Environment Issues

If `python3.13 -m venv` fails:

```bash
# Reinstall venv package
sudo apt install --reinstall python3.13-venv

# Or create without pip and install manually
python3.13 -m venv .venv --without-pip
source .venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Debian Package Conflicts

The backport packages are designed to coexist with system Python. If you encounter conflicts:

1. Keep your system Python 3.11 intact
2. Only use Python 3.13 in virtual environments
3. Don't modify Debian's python3 alternatives

## Architecture-Specific Notes

### ARM64 (This System)

- **Fully supported** with pre-built wheels for most packages
- Fast installation times
- All Home Assistant dependencies available

### ARM32 (armhf)

- Requires additional dependencies: `rustc`, `ninja-build`, `cmake`, `libopenblas0`
- Longer installation times (compile from source)
- Consider upgrading to 64-bit OS for better performance

### AMD64

- Best support and fastest performance
- All wheels available pre-built

## VS Code Extensions Compatibility

All Python extensions work with Python 3.13:

- ✅ **Python** (ms-python.python)
- ✅ **Pylint** (ms-python.pylint)
- ✅ **Mypy Type Checker** (ms-python.mypy-type-checker)
- ✅ **Ruff** (charliermarsh.ruff)
- ✅ **Black Formatter** (ms-python.black-formatter)
- ✅ **isort** (ms-python.isort)

## Related Documentation

- [Linter Configuration](./LINTER_CONFIGURATION.md) - How ha-core is excluded from linting
- [Home Assistant Installation Guide](https://www.home-assistant.io/installation/linux#install-home-assistant-core)
- [Python 3.13 Backport Repository](https://community.home-assistant.io/t/python-3-13-backport-for-debian-12-bookworm/842333)

## Credits

Python 3.13 backport maintained by [@pascallj](https://community.home-assistant.io/u/pascallj) as a community service for Home Assistant Core users on Debian. This is the fourth in a series of Python backports (3.8, 3.10, 3.12, 3.13) enabling core installations on stable Debian releases.

---

**Last Updated**: November 17, 2025
**Python Version**: 3.13.2
**Package Version**: 3.13.2-1~bpo12+2

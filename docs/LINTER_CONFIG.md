# Development Environment Configuration Summary

## Python 3.13 Setup

**Python 3.13.2** is now installed from the community backport repository for Debian 12 Bookworm.

- **Installation script**: `/opt/docker/home-assistant/scripts/install-python313.sh`
- **System Python**: 3.11.2 (Debian default, unchanged)
- **Development Python**: 3.13.2 (Backport, for HA development)
- **Location**: `/usr/bin/python3.13`
- **VS Code default**: Configured to use Python 3.13

**Source**: [Python 3.13 backport for Debian 12](https://community.home-assistant.io/t/python-3-13-backport-for-debian-12-bookworm/842333)

## ha-core Linter Filtering

The workspace has been configured to **exclude the upstream Home Assistant core (`ha-core/`) from all linting and search operations** while maintaining full import resolution capabilities.

### Key Changes

1. **`/opt/docker/home-assistant/pyproject.toml`** - NEW
   - Root-level linter configuration
   - Excludes `ha-core/` from Ruff, Mypy, Pylint, and Pytest
   - Applies workspace-wide baseline exclusions

2. **`/opt/docker/home-assistant/home-assistant.code-workspace`** - UPDATED
   - Enhanced Pylance analysis exclusions
   - Added linter args for pylint, mypy, ruff
   - Excluded `ha-core` from file explorer and search

3. **`/opt/docker/home-assistant/.vscode/settings.json`** - UPDATED
   - Added Python analysis ignore patterns
   - Configured file watcher exclusions
   - Enhanced search exclusions
   - **Preserved**: `python.analysis.extraPaths` for import resolution

4. **`/opt/docker/home-assistant/.ignore`** - NEW
   - Ripgrep/fd exclusion file
   - Filters `ha-core/` from external search tools
   - Excludes common build artifacts and caches

### What Still Works

✅ **Import Resolution**: All `from homeassistant.*` imports work correctly
✅ **Autocomplete**: IntelliSense provides completions from ha-core
✅ **Type Checking**: Type hints from homeassistant are recognized
✅ **All Linters**: Ruff, Pylint, Mypy, and Black all still function
✅ **Testing**: Pytest can still import homeassistant modules

### What's Filtered Out

🚫 **Linter Errors**: No errors/warnings from ha-core files
🚫 **Search Results**: Workspace search excludes ha-core
🚫 **File Watching**: VS Code doesn't watch ha-core for changes
🚫 **Problems Panel**: Clean view of only your code's issues

### Verification

Reload VS Code window to apply all changes:
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### Documentation

Complete details in:
- `/opt/docker/home-assistant/home-assistant/config/docs/setup/LINTER_CONFIGURATION.md`

### Configuration Hierarchy

```
Root pyproject.toml          → Workspace-wide baseline
  └── Workspace settings     → VS Code multi-root config
       └── .vscode/settings  → Root folder settings
            └── Project configs → Per-project overrides (keymaster, etc.)
```

Each level can extend or override the previous level's configuration.

---
*Updated: November 17, 2025*

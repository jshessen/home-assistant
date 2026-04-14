# Linter Configuration for ha-core Exclusion

## Overview

This workspace includes the upstream Home Assistant core (`ha-core/`) as a read-only dependency for import resolution and reference. To prevent linter noise from upstream code, this configuration filters out `ha-core/` from all linting and search operations while maintaining full import capabilities.

## Configuration Files

### 1. Root `pyproject.toml`

**Location:** `/opt/docker/home-assistant/pyproject.toml`

This file provides workspace-wide linter configuration for:
- **Ruff**: Python linter and formatter with `exclude = ["ha-core", "ha-core/**"]`
- **Mypy**: Type checker with `exclude = ["^ha-core/"]`
- **Pylint**: Code quality checker with `ignore = ["ha-core"]`
- **Pytest**: Test discovery with `norecursedirs = ["ha-core"]`

Each tool is configured to completely ignore the `ha-core/` directory while allowing Python to resolve imports from it.

### 2. VS Code Workspace Settings

**Location:** `/opt/docker/home-assistant/home-assistant.code-workspace`

Multi-root workspace configuration that:
- **Excludes ha-core from Pylance analysis**: `python.analysis.exclude` and `python.analysis.ignore`
- **Passes exclusion args to linters**: `pylint.args`, `mypy-type-checker.args`
- **Hides from file explorer**: `files.exclude` includes `"ha-core": true`
- **Excludes from workspace search**: `search.exclude` includes `"**/ha-core/**"`

### 3. Root `.vscode/settings.json`

**Location:** `/opt/docker/home-assistant/.vscode/settings.json`

Root-level VS Code settings that:
- **Maintains import paths**: `python.analysis.extraPaths` and `python.autoComplete.extraPaths` include `ha-core`
- **Excludes from analysis**: `python.analysis.exclude` and `python.analysis.ignore`
- **Reduces file watching**: `files.watcherExclude` prevents VS Code from watching `ha-core/` for changes
- **Excludes from search**: `search.exclude` filters out `ha-core`

### 4. `.ignore` File

**Location:** `/opt/docker/home-assistant/.ignore`

Ripgrep/fd exclusion file used by VS Code search and external tools. Excludes:
- `ha-core/` directory
- Python caches and build artifacts
- Virtual environments
- Home Assistant runtime files

## How It Works

### Import Resolution (Preserved)

Python imports from `homeassistant.*` work correctly because:

1. **Python path includes ha-core:**
   ```json
   "python.analysis.extraPaths": ["${workspaceFolder}/ha-core"]
   "python.autoComplete.extraPaths": ["${workspaceFolder}/ha-core"]
   ```

2. **Linters understand the path:**
   - Pylint: `ignored-modules = ["homeassistant", "homeassistant.*"]`
   - Mypy: `ignore_missing_imports = true` for flexible resolution

3. **Code can import normally:**
   ```python
   from homeassistant.core import HomeAssistant
   from homeassistant.helpers.entity import Entity
   ```

### Linting/Analysis (Filtered)

Linters skip `ha-core/` entirely:

1. **File-level exclusion:**
   - Ruff: `exclude = ["ha-core", "ha-core/**"]`
   - Mypy: `exclude = ["^ha-core/"]`
   - Pylint: `ignore = ["ha-core"]`

2. **Analysis exclusion:**
   - Pylance: `python.analysis.exclude` and `python.analysis.ignore`

3. **Search exclusion:**
   - Workspace search: `search.exclude`
   - File watcher: `files.watcherExclude`
   - Ripgrep: `.ignore` file

## Project-Specific Overrides

Individual projects (like `keymaster-github/`) can have their own `pyproject.toml` with extended configurations. The root config provides baseline exclusions that apply workspace-wide.

### Keymaster Example

The keymaster custom component has its own comprehensive `pyproject.toml` at `/opt/docker/home-assistant/keymaster-github/pyproject.toml` with:
- Extended ruff rules
- Detailed pylint configuration
- Full test configuration
- Its own `exclude = ["ha-core"]` settings

## Benefits

1. **No linter noise**: Errors/warnings from upstream code don't appear in your Problems panel
2. **Faster analysis**: VS Code skips thousands of upstream files during analysis
3. **Cleaner search**: Workspace search only shows your custom code
4. **Maintained imports**: All `homeassistant.*` imports work normally
5. **No functionality loss**: All linters and tools still work on your code

## Verification

To verify the configuration is working:

1. **Check import completion:**
   - Type `from homeassistant.` in a Python file
   - Autocomplete should show available modules

2. **Verify linting scope:**
   - Open a file in `ha-core/`
   - No linter errors should appear (or they'll be grayed out)
   - Open a file in your custom code
   - Linter errors should appear normally

3. **Test search exclusion:**
   - Search for a common term like "async"
   - Results should exclude `ha-core/` files

## Troubleshooting

### Imports Not Working

If imports from `homeassistant.*` show errors:

1. Check `python.analysis.extraPaths` includes `ha-core`
2. Verify the Python interpreter is configured: `/usr/bin/python3`
3. Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Linter Still Showing ha-core Errors

If you still see linter errors from `ha-core/`:

1. Check the linter args in workspace settings
2. Verify `pyproject.toml` excludes are in effect
3. Restart the linter: `Ctrl+Shift+P` → "Python: Restart Language Server"
4. Check for project-specific configs that might override exclusions

### Search Still Finding ha-core Files

If workspace search includes `ha-core/` files:

1. Verify `.ignore` file exists at root
2. Check `search.exclude` in workspace settings
3. Try toggling "Use Exclude Settings and Ignore Files" in search panel

## Related Files

- `/opt/docker/home-assistant/pyproject.toml` - Root linter config
- `/opt/docker/home-assistant/home-assistant.code-workspace` - Multi-root workspace settings
- `/opt/docker/home-assistant/.vscode/settings.json` - Root VS Code settings
- `/opt/docker/home-assistant/.ignore` - Ripgrep exclusions
- `/opt/docker/home-assistant/keymaster-github/pyproject.toml` - Keymaster-specific config

## Last Updated

November 17, 2025

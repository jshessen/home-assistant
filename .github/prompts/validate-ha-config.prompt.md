---
mode: "agent"
tools: ["run_in_terminal"]
description: "Validate Home Assistant configuration and report any errors"
---

Run the Home Assistant configuration check and report the results.

Execute this command:

```
timeout 30 docker exec home-assistant python -m homeassistant --script check_config -c /config 2>&1
```

Then:

1. If the output contains no errors, confirm that the configuration is valid and safe to restart.
2. If there are errors, list each error clearly with the file name and line number (if shown), and explain what likely caused it.
3. Remind the user: **configuration must be valid before restarting Home Assistant**. A failed config check means HA will not start after a restart.

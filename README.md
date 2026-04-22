# home-assistant
Container definition for hass.io services

---

## AI Team (Squad)

This repo uses [Squad](https://bradygaster.github.io/squad/) with a **personal/global squad** setup. Agents, charters, skills, and casting state live in the personal squad directory (`~/.config/squad/.squad/`) — not inside this repo. The project's `.squad/` folder contains only local state (decisions, logs, orchestration history) and a machine-local `config.json` pointer.

### Architecture

```
~/.config/squad/.squad/        ← personal squad (agents, charters, skills, casting)
    agents/
        iron-man/              ← HA Automation Engineer
        black-widow/           ← Integration Specialist
        doctor-strange/        ← Template Dev
        hawkeye/               ← Troubleshooter
        captain-america/       ← Project Steward
        nick-fury/             ← Lead
        vision/                ← AI & Emerging Tech
        scribe/                ← Session Logger (exempt from casting)
        ralph/                 ← Work Monitor (exempt from casting)
    casting/
    skills/
    routing.md
    team.md

/opt/docker/home-assistant/.squad/    ← project squad (local state only)
    decisions.md
    decisions/inbox/
    log/
    orchestration-log/
    config.json                       ← machine-local pointer (gitignored)
```

### Setting Up on a New Machine

The `squad-export.json` in the repo root is a portable snapshot of the full team. Import it into your **personal squad directory** — not into the project.

```bash
# 1. Install the Squad CLI
npm install -g @bradygaster/squad-cli

# 2. Create the personal squad directory
mkdir -p ~/.config/squad

# 3. Import the team into the personal squad
#    (run from the personal squad dir so Squad writes there)
cd ~/.config/squad
squad import /path/to/home-assistant/squad-export.json

# 4. In this project, initialize the remote pointer
cd /path/to/home-assistant
squad init --remote ~/.config/squad
```

After step 4, `.squad/config.json` will be created with:
```json
{ "version": 1, "teamRoot": "/home/<you>/.config/squad", "projectKey": null }
```
This file is gitignored — each machine has its own path.

### Keeping the Export Current

Re-export whenever the team changes (new agents, skills learned, decisions made):

```bash
cd /opt/docker/home-assistant
squad export          # overwrites squad-export.json
git add squad-export.json && git commit -m "chore: refresh squad export"
```

### Collision Handling

If the target personal squad already has agents (e.g., from another project), use `--force` to archive the existing team first:

```bash
cd ~/.config/squad
squad import /path/to/squad-export.json --force
```

The `--force` flag moves the existing team to an archive — nothing is deleted.

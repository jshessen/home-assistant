# Captain America Decision: Git Stewardship Routing and Hygiene Baseline

**Date:** 2026-04-21
**Author:** Captain America (Project Steward)
**Status:** Proposed

## Decision

Git repository stewardship is explicitly owned by Captain America and routed to Captain America by default for:
- git hygiene and cleanup planning
- repo hygiene checks (status, branch divergence checks, safe reconciliation)
- branch management and stale-branch cleanup workflows
- release changelog and release-tag preparation

## Why

Routing and ownership were partially implied but not consistently explicit. Making this ownership clear reduces handoff ambiguity and keeps non-destructive repo hygiene work centralized under the steward role.

## Immediate Baseline Findings

- `main` currently has no upstream tracking branch configured.
- Ahead/behind cannot be evaluated until tracking is set.
- Working tree is dirty across non-`.squad` domains; cleanup should proceed via split, focused commits.

## Team Impact

- Coordinators and members now have a default owner for Git hygiene and release-changelog workflow tasks.
- Repo cleanup proceeds via checklist-driven, non-destructive steps unless explicitly directed otherwise.

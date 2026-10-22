---
name: sync-from-game
description: For modkit maintainers - bring the modkit up to date after the game exported new schemas, reference content or game.json. Fills in new field meanings, rebuilds the bundles, runs the tests. Not for making mods.
---

# Sync from a game export

**Input:** a working tree where the game's export has rewritten `schemas/`, `reference/core/` and
`game.json`. **Output:** docs and bundles that cover every field, tests passing, one commit.

1. `git status` and `git diff --stat`: only `schemas/`, `reference/core/` and `game.json` changed.
   If anything else changed, stop and report.
2. Read the `game.json` diff. If `modApi` went up, note it for the changelog and check
   `workflows/update-for-new-game-version.md` still holds.
3. `python3 tools/modkit.py bundle`. It regenerates the field tables in `docs/api/`; fill in the
   meaning of every new field (the cells it leaves as TODO). *Check:* `python3 tools/modkit.py bundle --check` passes.
4. If a new capability shipped, update `docs/limits.md`.
5. `python3 -m unittest discover -s tests`, and for each example (furhats, tundrawolves, flax)
   `python3 tools/modkit.py validate NAME --local`, as CI does. *Done when:* all pass.
6. Add a line under `## Unreleased` in `CHANGELOG.md` (name the `modApi` if it changed), commit. Do
   not push unless asked.

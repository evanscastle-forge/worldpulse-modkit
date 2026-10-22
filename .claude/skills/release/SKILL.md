---
name: release
description: For modkit maintainers - cut a modkit version. Moves CHANGELOG Unreleased under a new SemVer version, bumps VERSION, commits and tags locally. Not for making mods.
---

# Release the modkit

**Input:** a clean tree with entries under `## Unreleased`. **Output:** a commit and local tag `vX.Y.Z`.

1. `git status` is clean; `python3 -m unittest discover -s tests` and
   `python3 tools/modkit.py bundle --check` pass. If not, stop and report.
2. Pick the version from `VERSION` and the Unreleased entries (pre-1.0: minor for new docs, tools
   or a new `modApi`; patch for fixes). Ask if unsure.
3. In `CHANGELOG.md`, rename `## Unreleased` to `## X.Y.Z - YYYY-MM-DD` and add a fresh empty
   `## Unreleased` above it.
4. Write `X.Y.Z` to `VERSION`.
5. `git commit -am "Release X.Y.Z"` and `git tag vX.Y.Z`. Do not push unless asked.

# Workflow: update a mod for a new game version

**Input:** a mod made for an older `modApi` or core content. **Output:** it validates and tests on
the current toolkit.

1. Update the toolkit (`git pull`), then `python3 tools/modkit.py doctor`: the toolkit and the game
   should agree.
2. `python3 tools/modkit.py validate MODID`. Fields that were renamed show as unknown fields with a
   "did you mean"; removed ones as unknown fields without one (see the game's release notes).
3. For every override in the mod, compare it with the new `reference/core/` version of that def
   (`git diff` the toolkit's `reference/core/` between versions shows what core changed). Take core's
   new values for every field you did not mean to change.
4. Set `modApi` in `mod.json` to the value in `game.json`. Raise the mod's `version`.
5. Follow `test-and-balance.md`.

*Done when:* validate and test are clean on the new version.

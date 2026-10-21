# Workflow: test and balance

**Input:** a mod that validates. **Output:** a passing `modkit test` and numbers that make sense.

1. Make sure `mods/MODID/tests/expect.json` exists (see `docs/testing.md`).
2. Run `python3 tools/modkit.py test MODID`. If it says the game was not found, tell the person how
   to set it up (`docs/testing.md`) and skip to step 5.
3. Read the report:
   - `NEVER <id>`: the def did not show up. Common causes: an animal no biome lists, a crop with
     `minTemp` above the landing site's climate, a recipe whose material never exists, a building
     without `costItem`. Fix and re-run. For a biome-specific mod, set `"biome"` in expect.json.
   - deaths or breaks you did not intend: the mod is too harsh (damage, manhuntChance, mood).
   - `FAIL the game failed on tick ...`: a crash; report it to the game with the mod attached.
4. Compare every number you set with `docs/balance.md`. Anything far outside the core range needs a
   reason in NOTES.md, or a change.
5. Tell the person what to try in the game (`modkit install MODID`) and what to look for.

*Done when:* `test` prints OK (or cannot run, and you said so), and NOTES.md explains every
out-of-range number.

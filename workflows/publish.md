# Workflow: publish

**Input:** a reviewed mod. **Output:** a zip to share.

1. `review.md` says APPROVE.
2. `mod.json`: `version` raised since the last release; `description` written for players.
3. `python3 tools/modkit.py pack MODID`. *Check:* it prints `wrote dist/MODID-VERSION.zip`.
4. Tell the person: the zip goes into the players' mods folder (`modkit doctor` shows where), and
   what to mention when sharing it (what it overrides, the game version).

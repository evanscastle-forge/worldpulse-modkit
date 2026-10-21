# Workflow: add one def

**Input:** one row of the spec. **Output:** the def in the mod, validated.

1. Copy the closest def: `python3 tools/modkit.py new-def KIND NAME --like COPY_ID --mod MODID`.
   For an override: `python3 tools/modkit.py override CORE_ID --mod MODID` (copies it whole, keeps its id).
2. Open `docs/api/KIND.md`. Change only fields in its table. Set `label`, `color` and the numbers
   the idea is about. Keep everything else as copied.
3. Check every id the def points at exists (`docs/ids.md`, or the mod's own defs). Sprites can stay
   pointing at core sprites until you draw your own.
4. Read the "used automatically when" section of `docs/api/KIND.md`. If the def needs something to
   reach the game (a biome listing an animal, a recipe for an item, `sowable` for a crop), do that too.
5. `python3 tools/modkit.py validate MODID`. Fix all errors (`fix-validation-errors.md`).
6. Add a row for it to NOTES.md if it isn't there.

*Done when:* validate shows no errors for this def, and no "will never appear" warning.

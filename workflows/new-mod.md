# Workflow: a new mod, from idea to playable

**Input:** an idea in the person's words. **Output:** a mod folder that validates, tests clean, and a
short report.

1. Pick a mod id: one lowercase word from the idea (`furhats`, `tundrawolves`). Run
   `python3 tools/modkit.py new MODID --name "Display Name"`.
   *Check:* `mods/MODID/mod.json` exists.
2. Follow `idea-to-spec.md`. *Done when:* `mods/MODID/NOTES.md` has the spec and the person agreed.
3. For each def in the spec, in this order (materials before what uses them, sprites last):
   terrain, plant, item, building, animal, biome overrides, weather, thought overrides, sprites.
   Follow `add-def.md` for each; `make-sprite.md` for each sprite.
   *Check after each:* `python3 tools/modkit.py validate MODID` has no errors.
4. Write `mods/MODID/tests/expect.json`: one `seen` entry per new item, plant, animal or building,
   and `{ "metric": "deaths", "max": 0 }` unless the mod is meant to be dangerous. If the mod is about
   one biome (it overrides a biome, or adds a crop or animal for one), set `"biome"` to that biome's
   id so every test lands there.
5. Follow `test-and-balance.md`.
6. Follow `review.md`. Fix what it finds.
7. Fill in `mods/MODID/README.md` for players (what it adds, what it overrides).
8. Report to the person in this shape:

```
Made: <mod name> (<n> defs) — <one sentence>
Try it: python3 tools/modkit.py install MODID   (then look for <what to look for in the game>)
Could not do: <anything that needs a game update, with the feature request> | nothing
Checks: validate OK, test <passed | not run: game not found>
```

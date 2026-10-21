# AGENTS.md: instructions for the AI assistant

You help a person make a **mod** for the game WorldPulse, a colony sim. A mod is a folder of JSON
files (defs) and pixel-art sprites. You write those files; the person plays the result. Follow these
instructions exactly. When they conflict with what you think is best, follow them anyway.

## Rules that never bend

1. **Only use fields that are in the docs.** Each kind has a field table in `docs/api/<kind>.md`.
   The game silently ignores any other field, so an invented field does nothing. Never invent one.
2. **Ids are `<modid>.<kind>.<name>`**, lowercase, words joined by `_`: `furhats.item.fur_hat`.
   The mod id is the mod's folder name and the `id` in its `mod.json`.
3. **Whole numbers only.** No decimals anywhere. Time is in ticks: 20 per second, 6000 per day.
4. **Never edit `reference/`, `schemas/`, `game.json` or `tools/`.** They describe the game. To
   change a core def, copy it whole into the mod and change the copy.
5. **Validate after every change**: `python3 tools/modkit.py validate MODID`. Fix every ERROR before
   doing anything else. Fix or explain every WARNING (in NOTES.md). The messages say what to do.
6. **Mods are data, not code.** If the idea needs new behaviour (a new thought trigger, a building
   that does something new, a new job, scripts), say so plainly, check `docs/limits.md`, build the
   part that is data, and write the rest as a feature request. Never pretend.
7. **Start from a copy.** For a new def, copy the closest existing one:
   `python3 tools/modkit.py new-def KIND NAME --like CORE_ID --mod MODID`, then edit it.
8. **Keep NOTES.md up to date**: what the mod is, every def and why, every core override and why,
   every number that is outside `docs/balance.md` ranges and why.

## Where things are

| path | what |
| --- | --- |
| `docs/concepts.md` | how mods work: ids, kinds, load order, overriding, units. **Read first.** |
| `docs/api/*.md` | every field of every kind, with types, defaults and meaning |
| `docs/ids.md` | every id in the game's core content |
| `docs/limits.md` | what needs a game update |
| `docs/balance.md` | the numbers core uses: stay near them |
| `docs/art.md` | how to draw sprites |
| `docs/testing.md` | validate, test, expect.json |
| `reference/core/` | the game's own content, the best examples there are |
| `workflows/*.md` | step-by-step procedures (below) |
| `agents/*.md` | role cards: designer, author, artist, tester, reviewer |
| `mods/` | the person's mods (`modkit new` creates them here) |
| `examples/` | finished example mods |

## Which workflow

| the person wants to... | follow |
| --- | --- |
| start a mod from an idea | `workflows/new-mod.md` (it calls the others) |
| turn a vague idea into a plan | `workflows/idea-to-spec.md` |
| add an item, plant, building, animal, ... | `workflows/add-def.md` |
| draw or change a sprite | `workflows/make-sprite.md` |
| fix validator errors | `workflows/fix-validation-errors.md` |
| see if it works and is balanced | `workflows/test-and-balance.md` |
| check a mod before it is shared | `workflows/review.md` |
| update a mod after a game update | `workflows/update-for-new-game-version.md` |
| share it | `workflows/publish.md` |

## The loop

1. **Understand.** Restate the idea in one or two sentences. Ask at most three questions, only about
   things that change what you build.
2. **Spec.** Write the plan in the mod's `NOTES.md`: each def with its id and purpose, each override.
3. **Smallest step.** Add one def. Validate. Fix. Repeat for the next def.
4. **Test.** `python3 tools/modkit.py test MODID` if the game is installed (it says if not). Read the
   report: did every def show up? Did anyone die who shouldn't have?
5. **Review.** Go through `workflows/review.md` yourself before saying you are done.
6. **Report.** Tell the person what you made, what you could not (and why), and how to try it.

## Commands

```
python3 tools/modkit.py new MODID --name "Display Name"     # new mod in mods/MODID
python3 tools/modkit.py new-def item fur_hat --like core.item.tuque --mod MODID
python3 tools/modkit.py override core.biome.tundra --mod MODID   # to change a core def
python3 tools/modkit.py validate MODID                      # after every change
python3 tools/modkit.py sprite MODID.sprite.x --mod MODID    # look at a sprite
python3 tools/modkit.py test MODID                          # the game plays it (needs the game)
python3 tools/modkit.py install MODID                       # put it in the game (reloads it live)
```

## Inside the game's agent panel

When messages start with `[panel tick=... day ... paused=... cursor=(x,y) selected=...]`, you are in
the panel beside the running game:

- Reply in **one to three short lines**.
- To change the mod: make the edit, validate, then end with exactly one line
  `PROPOSE: <what> | expect: <what the player will see>` and stop. Do not install it yourself.
- `[panel] The player typed yes ...` means it was installed: say what to look for, in one line.
- If the player's next message is anything other than `yes`, nothing was applied: undo your
  unapplied edit unless they ask to keep working on it.
- `back` restored the previous version: say so and undo the source change.
- `keep` asks you to turn the player's note into an entry in `tests/expect.json`.

## When you are unsure

- A field's meaning: `docs/api/<kind>.md`, then the core defs in `reference/core/` that use it.
- Whether something is possible: `docs/limits.md`. If it is not listed and not in the field tables,
  assume it is not possible and say so.
- A number: `docs/balance.md`.

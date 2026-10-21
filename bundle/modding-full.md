# WorldPulse modding (full)

Everything an AI assistant needs to write WorldPulse mods, in one file. Game: mod API 1, core content e5a94f1feb3c.
Paste or attach this file, then describe the mod you want. Follow the rules in AGENTS.md exactly.

---
<!-- file: README.md -->

# WorldPulse Modkit

**Make mods for WorldPulse by describing them to an AI.**

WorldPulse is a colony sim on a globe of hex tiles: colonists with six RPG attributes and growing
skills, a licence-style ID card each, apparel they make and wear, wildlife, rooms, seasons, all in
pixel art. Everything in the game (every plant, animal, item, building, biome, thought, and every
sprite) is plain JSON. So a mod is plain JSON too, and an AI assistant is very good at writing it.

This toolkit is everything an assistant needs to do that well: the rules, a reference for every
field, step-by-step workflows, role cards, prompts for chat assistants, and a validator whose every
message says how to fix the problem. It works with a coding agent, with a chat window, or with a
small local model.

```
you:    "Add fur hats made from leather at the tailor bench. Warmer than a tuque."
agent:  writes mods/furhats/defs/items.json and a sprite, validates, tests, reviews
you:    python3 tools/modkit.py install furhats      # it's in your running game
```

## Three ways to use it

**1. A coding agent** (Claude Code, Codex, Cursor, Aider, Copilot...). Open this folder in it and ask
for your mod. It reads [AGENTS.md](AGENTS.md) and runs the tools itself.

**2. Any chat assistant.** Attach [bundle/modding-small.md](bundle/modding-small.md) (or
[the full one](bundle/modding-full.md)), then use the prompts in [prompts/](prompts/): describe your
idea, paste the JSON it writes into files, run the validator, paste the output back. Works with
small and local models. See [docs/small-models.md](docs/small-models.md).

**3. Inside the game** (coming). The game has an agent panel beside the map: type "make wolves
rarer", type `yes`, and it's in your game on the same tick. The panel will run this toolkit's
instructions with the model of your choice ([docs/panel-protocol.md](docs/panel-protocol.md)).

## Quickstart

You need Python 3.8+ (nothing else to install) and, for the in-game tests, WorldPulse.

```
git clone <this repository> worldpulse-modkit && cd worldpulse-modkit
python3 tools/modkit.py doctor                  # finds the game and your mods folder
python3 tools/modkit.py new furhats --name "Fur Hats"
```

Then, with a coding agent: *"Make the furhats mod: a fur hat made from leather at the tailor bench,
warmer than a tuque, with its own sprite. Follow AGENTS.md."*

Or by hand:

```
python3 tools/modkit.py new-def item fur_hat --like core.item.tuque --mod furhats
#   edit mods/furhats/defs/items.json: label, color, "cold": 9, recipe item core.item.leather
python3 tools/modkit.py validate furhats        # every message says what to fix
python3 tools/modkit.py test furhats            # the game plays it for 10 days and reports
python3 tools/modkit.py install furhats         # into your game
```

## What's in here

| | |
| --- | --- |
| [AGENTS.md](AGENTS.md) | the assistant's instructions: rules, the loop, which workflow when |
| [docs/](docs/) | [concepts](docs/concepts.md), [every field of every kind](docs/api/), [limits](docs/limits.md), [balance](docs/balance.md), [art](docs/art.md), [testing](docs/testing.md), [publishing](docs/publishing.md) |
| [workflows/](workflows/) | step-by-step procedures: new mod, add a def, draw a sprite, fix errors, test, review, publish |
| [agents/](agents/) | role cards: designer, author, artist, tester, reviewer |
| [prompts/](prompts/) | copy-paste prompts for chat assistants |
| [bundle/](bundle/) | everything in one file, to attach to a chat |
| [examples/](examples/) | finished mods: fur hats, tundra wolves, flax |
| [reference/core/](reference/core/) | the game's own content, to read and copy from |
| [schemas/](schemas/) | JSON Schema for every def kind |
| [tools/modkit.py](tools/modkit.py) | the one script: new, validate, test, sprite, install, pack |

## What mods can do

Add or change terrain, biomes, plants and crops, items and food, apparel and recipes, buildings
(walls, beds, workbenches, heaters), animals, weather, the strength of thoughts, colonist settings,
attributes and skill weights, and every sprite. New *behaviour* (new jobs, new thought triggers,
scripted events) needs the game; [docs/limits.md](docs/limits.md) says what, and the agent will tell
you instead of pretending.

## Licence

The toolkit (docs, prompts, tools, templates, examples) is MIT: fork it, adapt the agent setup for
your own game. `reference/` is the game's content, published for modding only
([reference/LICENSE](reference/LICENSE)).

---
<!-- file: AGENTS.md -->

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

---
<!-- file: docs/concepts.md -->

# How WorldPulse mods work

WorldPulse is a colony sim on a globe of hex tiles. The whole game world is described by **defs**:
small JSON objects for each terrain, biome, plant, item, building, animal, weather, thought and
sprite. The game's own content is just the first mod, called `core`. A mod is a folder of more defs.

## A mod is a folder

```
furhats/
  mod.json            who made it, its version, what it needs   (not loaded as content)
  defs/items.json     defs: one object, or a list of them
  defs/sprites.json   pixel art, also defs
  flags.json          optional feature switches: { "name": true }
  tests/expect.json   what `modkit test` checks                  (not loaded as content)
  NOTES.md            the design notes you and your assistant keep
  README.md           for players
```

The game reads every `.json` file in the folder (any subfolder, any name) except `mod.json`,
`flags.json` (read as flags) and the `tests/` folder. File names must be lowercase. Comments
(`//`, `/* */`) and trailing commas are allowed.

## Every def has an id and a kind

```json
{ "id": "furhats.item.fur_hat", "kind": "item", "label": "fur hat", "color": "#8a6a4a" }
```

- **id**: `<mod id>.<kind>.<name>`, lowercase, words joined by `_`. The mod id is the folder name
  and the `id` in `mod.json`. Ids are how defs point at each other; never reuse one by accident.
- **kind**: one of `terrain biome plant item building weather animal roof thought sprite`. A def
  without a known kind is never used.
- A few defs are **singletons**, read by their fixed id instead of by kind: `core.colonist`,
  `core.worldgen`, `core.names`, `core.rpg`, `core.looks`, `core.rooms` (see `docs/api/singletons.md`).
- Field names are camelCase and case-sensitive. **A field the game does not know is ignored without
  a word**, so the validator treats an unknown field as an error. A field you leave out takes its
  default (listed in each `docs/api/` page). To leave yourself a note inside a def, start the field
  name with `_`: `"_why": "warmer than a tuque"`.

## Load order and overriding

`core` loads first, then mods (by `load-order.txt` in the mods folder if the player has one, else by
name, each after the mods its `mod.json` lists in `loadAfter`). **A def with the same id as an
earlier one replaces it completely.** There is no "change one field": to change the tuque's warmth,
copy the whole `core.item.tuque` def into your mod and edit the copy. Two mods that override the same
def conflict; the later one wins (see `docs/compatibility.md`).

## Numbers and units

Everything is a whole number. No decimals anywhere.

| quantity | unit |
| --- | --- |
| time | ticks: 20 per second of game time, 6000 per in-game day |
| percentages | 100 = normal (`pathCost` 150 = half again as slow) |
| needs (food, rest) | 0..1000; a colonist uses about 700 food a day, a meal gives 900 |
| mood | 0..100; thoughts add or subtract points |
| temperature | whole degrees Celsius |
| health | points; a colonist has about 100 |
| chances | per mille (out of 1000) where noted, else percent |
| colors | `"#rrggbb"` |

## What happens when a mod loads

Content arrives in the game as one logged step, so a save replays exactly with the content that was
live at each moment. A running game picks up a changed mod with `modkit install` (which reloads it
live). Some things only happen when something is generated:

- **The globe** (where biomes are) is generated once, when a new game starts. Biome edits affect new
  games only.
- **A tile's map** (plants, rock, animals) is generated when the colony first enters that tile. New
  plants and animals appear on maps generated after the mod loads, and through normal growth,
  spreading and animal arrivals on existing maps.
- Everything else (item stats, building costs, recipes, thoughts' strength, colonist settings)
  applies from the moment the mod loads.

## Data, not code

A mod changes **data**: numbers, lists, new things of existing kinds, pixel art. It cannot add new
**behaviour**: a new kind of job, a new trigger for a thought, a building that does something no
building does today. When an idea needs behaviour, say so plainly and see `docs/limits.md`.
Scripting is planned; it is not here yet.

---
<!-- file: docs/limits.md -->

# What a mod can't do (yet)

Mods change data. These need a game update. When an idea needs one of them, say so plainly, build
the part that *is* data, and write the rest up as a feature request (template below). **Never invent
a field to fake it**: the game ignores unknown fields, so it would silently do nothing.

| idea | why it needs the game | what a mod can do today |
| --- | --- | --- |
| a new thought ("admired the sunset") | thoughts are triggered by game code | change the mood and duration of a built-in thought |
| a building that does something new (well, trap, turret, research desk) | behaviour lives in code; `use` only knows `bed door craft` | a decorative building; a craft station for new recipes; a heater/cooler via `heat` |
| a recipe that makes food, or several outputs, or uses two materials | a recipe is one material in, one item out | single-material recipes for any item, at any `craft` station |
| new work types, jobs or skills | the eight work types are fixed | retune skill weights in `core.rpg` |
| new attributes | the six are read by key | relabel and recolor them |
| animal behaviour (tame, herd, flee from fire) | animal AI is code | stats: speed, damage, diet, temperature range, retaliation |
| events (raids, traders, disasters) | not in the game yet | none |
| changing one field of a core def | defs are replaced whole | copy the whole def and change the field |
| adding to a core list (a biome's animals) without copying it | no patch operation yet | copy the whole biome def |
| sounds, music, UI changes | not moddable yet | none |
| scripts / code | scripting is planned, not available | none |

Planned: list-append patches (add to a biome's `plants` without copying it), new thought triggers
from data, and a scripting layer. `docs/game-contract.md` tracks these.

## Feature request template

```
Feature request for WorldPulse (mod API <modApi from game.json>)
Mod: <id> — <one line about the mod>
Wanted: <what the game would need to do>
Why data can't do it: <which limit above>
Smallest version that would help: <e.g. "a building use 'well' that colonists drink from">
```

---
<!-- file: docs/compatibility.md -->

# Playing well with other mods

- **Use your own ids.** Everything new starts with your mod id: `furhats.item.fur_hat`. Two mods
  with different ids never collide.
- **Overriding is all or nothing.** A def with an existing id (`core.biome.tundra`) replaces it
  completely. If two mods override the same def, the one that loads later wins and the other's
  change is lost. The validator lists your overrides; keep them few and say why in NOTES.md.
- **Biomes are the usual clash.** Adding a plant or animal to a biome means overriding the biome.
  Mention it in your README ("overrides the tundra biome") so players know.
- **Load order.** Mods load by name unless the player has a `load-order.txt`, and after the mods in
  your `mod.json` `loadAfter`. Put a mod there when your override should win over theirs.
- **Building on another mod.** List it in `requires`; refer to its ids freely. The tools load it
  first when checking (put it beside yours or in `mods/`).
- **Game updates.** `game.json` pins the game version this toolkit was made for. When the game's
  `modApi` changes, re-run `modkit validate`: renamed fields show up as unknown fields with a "did
  you mean". When only core content changes, overrides you copied may be stale: compare them with
  `reference/core/` (workflow `update-for-new-game-version.md`).

---
<!-- file: docs/balance.md -->

# Balance: numbers from the game

Pick numbers near what the game already uses. These tables come from `reference/core/` (regenerated
by `modkit bundle`), so they match the pinned game version. Going outside a range is fine when you
mean it: write why in NOTES.md, then check it with `modkit test`.

Rules of thumb:
- One in-game day is 6000 ticks. A crop that takes 4 days has `growTicks` about 24000.
- A colonist uses about 700 food a day (the food need runs 0..1000). A cooked meal is 900; raw
  food is 50 per unit.
- Apparel: a tunic is `cold` 3; a parka is `cold` 18. The leather vest's `armor` 25 is strong.
- Predators: `damage` 9 with `manhuntChance` 6 (the wolf) is already dangerous to a small colony.

**plant** (12 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `growTicks` | 12000 | 30000 | 100000 | 30000 |
| `harvestYield` | 8 | 11 | 12 | 0 |
| `woodYield` | 10 | 26 | 32 | 0 |
| `nutrition` | 150 | 250 | 260 | 0 |
| `minTemp` | -8 | 2 | 8 | 1 |
| `maxTemp` | 55 | 55 | 55 | 45 |
| `workTicks` | 30 | 60 | 200 | 60 |

**item** (16 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `nutrition` | 50 | 50 | 900 | 0 |
| `stackLimit` | 1 | 75 | 75 | 75 |
| `cold` | 0 | 4 | 18 | 0 |
| `heat` | -4 | 1 | 6 | 0 |
| `armor` | 25 | 25 | 25 | 0 |

**building** (13 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `costCount` | 5 | 25 | 50 | 0 |
| `workTicks` | 100 | 200 | 320 | 100 |
| `heat` | -40 | 15 | 60 | 0 |

**animal** (9 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `maxHealth` | 20 | 75 | 170 | 50 |
| `damage` | 2 | 8 | 16 | 5 |
| `attackTicks` | 40 | 45 | 55 | 50 |
| `moveTicks` | 4 | 4 | 5 | 6 |
| `meatYield` | 8 | 30 | 80 | 20 |
| `leatherYield` | 4 | 20 | 40 | 0 |
| `size` | 40 | 70 | 110 | 70 |

**thought** (22 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `mood` | -15 | -4 | 10 | 0 |
| `ticks` | 120 | 600 | 18000 | 6000 |

**weather** (6 in core)

| field | min | typical | max | default |
| --- | --- | --- | --- | --- |
| `weight` | 5 | 25 | 50 | 10 |
| `tempOffset` | -3 | -2 | -1 | 0 |
| `growth` | 50 | 90 | 125 | 100 |

---
<!-- file: docs/art.md -->

# Pixel art

WorldPulse's art is tiny pixel sprites stored as text in sprite defs (`docs/api/sprite.md`). An
assistant can draw them, and `python3 tools/modkit.py sprite ID --mod MYMOD` shows the result in the
terminal (or `--png out.png` for a picture to look at or paste into a chat).

## The house style

- **A dark outline** `#1b1f24` (palette key `k`) around every shape. It is what makes things
  readable on any ground.
- **Few colors**: a main color, a darker shade for the bottom/shadow side, a lighter one for the
  top-left highlight. Light comes from the top left.
- **Use tints, not fixed colors**, for anything that should take the def's color: `$main`, `$main-`
  (darker), `$main+` (lighter). One sprite then serves many items or animals (all core animals
  share six silhouettes).
- **Sizes**: 16×16 for anything on the map, 32×32 for ID-card portraits, 8×8 for attribute icons.
  At 16px a hat is 4 rows tall; don't try to draw details smaller than 2 pixels.
- Leave transparent space (`.`) around a thing on the ground: items sit in the middle of their cell.

## Worn apparel must line up with the body

A worn `layer` is drawn on top of the 16px body below, so hats cover rows 0..4, tops rows 8..12,
legs rows 12..15. Draw the layer with the body in mind and leave every other pixel `.`.

```
core.sprite.body                 core.sprite.wear.tuque (a hat layer)
................  row 0          .......ll.......
.....kkkkkk.....                 ....kmmmmmmk....
....kssssssk....                 ....kmmmmmmk....
....kssssssk....                 ....kMMMMMMk....
....kskssksk....  eyes           ................
....kssssssk....                 ................
....kSssssSk....                 ................
.....kkSSkk.....                 ................
....kuuuuuuk....  row 8: shirt   ................
...ksuuuuuusk...                 ................
...ksuuuuuusk...                 ................
...kskuuuuksk...                 ................
....kddddddk....  row 12: legs   ................
....kddkkddk....                 ................
....kSSkkSSk....                 ................
....kffkkffk....  row 15: feet   ................
```

Body palette: `k` outline, `s` `$skin`, `S` `$skin-`, `u` undershirt, `d` trousers, `f` feet. The
32px portrait is a head and shoulders: hats sit on rows 0..12 of the portrait; look at
`core.sprite.portrait.tuque` and `core.sprite.portrait.head` in `reference/core/sprites/`.

## A worked example: a fur hat

```json
{ "id": "furhats.sprite.wear.fur_hat", "kind": "sprite", "size": 16,
  "palette": { "k": "#1b1f24", "m": "$main", "M": "$main-", "l": "$main+", "w": "#e9e2d0" },
  "rows": [
    "....kwwwwwwk....",
    "...kwlmmmmlwk...",
    "...kmmmmmmmmk...",
    "...kwMMMMMMwk...",
    "................", "................", "................", "................",
    "................", "................", "................", "................",
    "................", "................", "................", "................" ] }
```

Check it: every row is 16 characters, every character is in the palette or `.`, and the preview
looks like a hat on a head (`modkit sprite furhats.sprite.wear.fur_hat --mod furhats`).

## Drawing tips for assistants

1. Start from the closest core sprite (`reference/core/sprites/`), copy it, and change it. That
   keeps the size, outline and alignment right.
2. Write the rows, then count: exactly `size` rows of exactly `size` characters.
3. Preview, look, adjust. Two or three rounds is normal.

---
<!-- file: docs/testing.md -->

# Testing a mod

Two layers. Run the first after every change; run the second before you call the mod done.

## Layer 1: `modkit validate` (no game needed)

```
python3 tools/modkit.py validate furhats
```

Checks against the schemas and the core content in this toolkit: unknown or misspelled fields, wrong
value types, ids that don't exist (with a "did you mean"), the wrong kind or sprite size, sprite grids,
apparel without a worn layer, and things the game will never use (an animal no biome lists, an item
nothing makes, a new thought). Every message says how to fix it. Errors must be fixed; warnings
should be fixed or explained in NOTES.md; notes are information.

If the game is installed and found (`modkit doctor`), `validate` also runs the game's own check.

## Layer 2: `modkit test` (needs the game)

```
python3 tools/modkit.py test furhats
```

Runs the game's `modtool validate`, then `modtool simulate`: the game plays your mod in an
unattended colony for some days on a few seeds, and reports

- whether each of your defs **showed up** (an item existed, a plant grew, an animal appeared, a
  building was built, a thought was felt), the most at once, and the first day;
- deaths, breakdowns and mood, so you can see if you made the game too hard or too easy;
- crashes, if any.

After landing, the simulated colony is given a starter setup for your mod: your buildings and the
stations of your recipes are placed, your recipes get bills of 2, your sowable plants get growing
zones, and your animals are hunted when they appear. Nothing else is done for it.

### tests/expect.json

What must hold for the mod to pass. `modkit test` (and the game) read it.

```json
{
  "days": 10,
  "seeds": [1, 2, 3],
  "biome": "core.biome.tundra",
  "expect": [
    { "metric": "seen", "id": "furhats.item.fur_hat", "min": 2 },
    { "metric": "deaths", "max": 0 },
    { "metric": "moodAvg", "min": 40 }
  ]
}
```

| metric | value | default check |
| --- | --- | --- |
| `seen` (needs `id`) | how many seeds it showed up in | at least 1 |
| `peak` (needs `id`) | the most of it at once, best seed | at least 1 |
| `deaths` | colonist deaths, worst seed | |
| `alive` | colonists alive at the end, worst seed | |
| `breaks` | breakdowns, worst seed | |
| `moodAvg` | average mood, worst seed | |
| `moodMin` | lowest mood, worst seed | |

`biome` lands every seed in that biome (the tools search for seeds that do), for mods about one place.
`days`, `seeds` and `biome` can be overridden: `modkit test furhats --days 3 --seeds 1`.

## Layer 3: play it

`python3 tools/modkit.py install furhats` copies the mod into the game's mods folder and reloads a
running game; `restore`/`uninstall` undo it. Sprites, the ID card and how it *feels* are only
checked by playing.

---
<!-- file: docs/api/animal.md -->

# animal

Wild animals. Grazers eat plants; predators hunt smaller animals and, when starving, sometimes
colonists. Hunted, they leave meat and leather.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "animal" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb`; tints its sprite through `$main` |
| `size` | a whole number | 70 | drawing size, 100 = a person |
| `maxHealth` | a whole number | 50 | health points (a colonist has about 100) |
| `moveTicks` | a whole number | 6 | ticks per cell walked (lower is faster; colonists take 6) |
| `damage` | a whole number | 5 | per bite |
| `attackTicks` | a whole number | 50 | ticks between bites |
| `foodDecay` | a whole number | 6 | how fast it gets hungry |
| `diet` | one of grazer, predator | "grazer" | `grazer` eats plants with nutrition; `predator` hunts animals with less `maxHealth` and eats meat |
| `meatYield` | a whole number | 20 | meat left when killed |
| `meatItem` | item id | "core.item.meat" | what meat it leaves |
| `minTemp` | a whole number | -100 | arrives only above this temperature |
| `maxTemp` | a whole number | 100 | arrives only below this temperature |
| `retaliate` | a whole number | 0 | percent chance to fight back when hurt (else it flees) |
| `manhuntChance` | a whole number | 0 | predators: percent chance per try to go for a colonist when starving with no prey near |
| `leatherYield` | a whole number | 0 | leather left when killed |
| `leatherItem` | item id | "core.item.leather" | what leather it leaves |
| `sprite` | sprite id (16px) |  | how it looks (16px), tinted by `color`. Core has `core.sprite.animal.small`, `.deer`, `.boar`, `.canine`, `.feline`, `.bear` |

## The game uses it automatically when...

Only if a biome lists it in its `animals` table: on new maps at generation, and in arrivals from the
map edge over time. To add an animal to the boreal forest, override `core.biome.boreal_forest`
(copy it whole) and add `{"id": "mymod.animal.x", "weight": 10}` to its `animals`.

## Example: core.animal.wolf

```json
{
  "id": "core.animal.wolf",
  "kind": "animal",
  "label": "wolf",
  "color": "#8b8f96",
  "size": 70,
  "maxHealth": 75,
  "moveTicks": 4,
  "damage": 9,
  "attackTicks": 45,
  "foodDecay": 8,
  "diet": "predator",
  "meatYield": 30,
  "leatherYield": 20,
  "sprite": "core.sprite.animal.canine",
  "minTemp": -40,
  "maxTemp": 35,
  "retaliate": 100,
  "manhuntChance": 6
}
```

## Gotchas

- A dangerous predator (high `damage`, `manhuntChance`) can kill a colony. Run `modkit test` and
  check deaths.

---
<!-- file: docs/api/biome.md -->

# biome

What a tile of the globe is like, and what its colony maps are made of. The globe is generated
once per game: a new or changed biome only shows on new games, and on maps first visited after the
mod loads.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "biome" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb` on the globe |
| `glyph` | text | "?" | one letter for the text map of the globe |
| `water` | true or false | false | an ocean biome: only on sea tiles |
| `minTemp` | a whole number | -100 | the tile temperatures (degrees, yearly mean) the biome claims |
| `maxTemp` | a whole number | 100 | upper end of the temperature range |
| `minRain` | a whole number | 0 | the tile rainfall it claims: roughly 0 (desert) to 3000 (rainforest) |
| `maxRain` | a whole number | 100000 | upper end of the rainfall range |
| `priority` | a whole number | 0 | where ranges overlap, the higher priority wins |
| `habitability` | a whole number | 50 | 0..100: how good a landing site it is (the game lands colonies on good sites) |
| `plantDensity` | a whole number | 400 | how thickly wild plants grow: 300 sparse, 600 dense |
| `waterFraction` | a whole number | 30 | how wet its maps are, 0..400: 0 dry, 60 typical, 120 swampy |
| `marshFraction` | a whole number | 20 | how much marsh, 0..400: 40 typical, 250 a swamp |
| `terrain` | a list of objects |  | ground bands by fertility noise, in order: each band is used up to `upTo` |
| `terrain[].terrain` | terrain id | required | the terrain |
| `terrain[].upTo` | a whole number | required | top of the band on the 0..1000 noise; the last band should reach 1000 |
| `plants` | list of objects; each id is a plant id |  | wild plants and how often each appears |
| `plants[].id` | text | required | the plant |
| `plants[].weight` | a whole number | required | relative chance against the other entries |
| `animalDensity` | a whole number | 0 | wild animals on a map of the standard size (core uses 5 to 14) |
| `animals` | list of objects; each id is a animal id |  | animals that live here and arrive here |
| `animals[].id` | text | required | the animal |
| `animals[].weight` | a whole number | required | relative chance |

## Adding a plant or animal to an existing biome

There is no "append": copy the whole biome def into your mod, keep every field, and add your entry
to `plants` or `animals`. Your copy replaces the core one. Two mods that both do this to the same
biome conflict; see `docs/compatibility.md`.

```json
{
  "id": "core.biome.tundra",
  "glyph": "u",
  "kind": "biome",
  "label": "tundra",
  "color": "#9aa48c",
  "minTemp": -16,
  "maxTemp": -3,
  "priority": 4,
  "habitability": 25,
  "plantDensity": 300,
  "waterFraction": 50,
  "marshFraction": 30,
  "terrain": [{"terrain": "core.terrain.gravel", "upTo": 450}, {"terrain": "core.terrain.soil", "upTo": 1000}],
  "plants": [{"id": "core.plant.grass", "weight": 70}, {"id": "core.plant.bush", "weight": 20}, {"id": "core.plant.pine", "weight": 6}],
  "animalDensity": 8,
  "animals": [{"id": "core.animal.hare", "weight": 40}, {"id": "core.animal.elk", "weight": 30}, {"id": "core.animal.wolf", "weight": 15}, {"id": "core.animal.bear", "weight": 5}]
}
```

---
<!-- file: docs/api/building.md -->

# building

Everything on a cell that is not a plant or an item: natural rock and ore, walls, doors, beds, fires,
coolers, workbenches.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "building" |  | always this value |
| `label` | text | "" | name shown in the game and the build menu |
| `color` | text | "#ff00ff" | `#rrggbb` |
| `glyph` | text | "wall" | drawing without a sprite, and the build tool: `wall` (dragged as a line), `door`, `bed`, `campfire`, `fireplace`, `cooler`, `bench`, `rock`, `ore` |
| `passable` | true or false | false | pawns can walk through it |
| `pathCost` | a whole number | 100 | walking cost through it when passable, percent |
| `natural` | true or false | false | natural rock: generated by the map, mined, never built |
| `mineItem` | item id |  | natural: what mining gives |
| `mineYield` | a whole number | 0 | natural: how much |
| `costItem` | item id |  | what building it takes; a building with a `costItem` is in the build menu |
| `costCount` | a whole number | 0 | how much of it |
| `workTicks` | a whole number | 100 | construction work at normal speed |
| `use` | text |  | what colonists use it for: `bed` (sleep), `door` (passable room wall), `craft` (recipes are made here); `campfire`, `heater`, `cooler` are labels only |
| `ore` | true or false | false | natural: generated as ore veins inside rock |
| `product` | item id |  | a cooking station: turns raw food into this item |
| `productCount` | a whole number | 1 | how many per batch |
| `ingredients` | a whole number | 10 | raw food units per batch |
| `productTicks` | a whole number | 200 | work per batch at normal speed |
| `wall` | true or false | false | bounds rooms (rock and doors do too) |
| `heat` | a whole number | 0 | inside a room: warms it (negative cools) by this much |
| `heatTarget` | a whole number | 21 | the temperature it stops warming (or cooling) at |
| `sprite` | sprite id (16px) |  | how it looks (16px) |

## The game uses it automatically when...

- **Built**: any non-natural building with a `costItem` is in the build menu (key B).
- **Natural**: rock (`natural`) and ore (`natural` + `ore`) are placed by map generation on new maps.
- Behaviour comes only from the fields: `use`, `product`, `heat`, `wall`, `passable`. A building
  that should do something else (a well, a trap, a research desk) needs a game update.

## Example: core.building.tailor_bench

```json
{
  "id": "core.building.tailor_bench",
  "kind": "building",
  "label": "tailor bench",
  "color": "#9b7a4e",
  "glyph": "bench",
  "use": "craft",
  "costItem": "core.item.wood",
  "costCount": 50,
  "workTicks": 200,
  "sprite": "core.sprite.building.tailor_bench"
}
```

---
<!-- file: docs/api/item.md -->

# item

Things that lie on the ground in stacks, get carried, eaten, worn and used as building material.
Food, materials (wood, stone, cloth, leather) and **apparel** are all items.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "item" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb`; also what `$main` means in its sprites (worn layers are tinted with it) |
| `stackLimit` | a whole number | 75 | most units on one cell; apparel should be 1 |
| `nutrition` | a whole number | 0 | food value per unit (the food need runs 0..1000); above 0 makes it food |
| `raw` | true or false | false | raw food: cooking stations turn it into meals; eating it raw gives the "ate raw food" thought |
| `meat` | true or false | false | predators eat it |
| `slot` | one of head, torso, legs, outer |  | makes it apparel, worn in this slot (one item per slot) |
| `cold` | a whole number | 0 | worn: degrees the comfortable range extends downward |
| `heat` | a whole number | 0 | worn: degrees the comfortable range extends upward |
| `armor` | a whole number | 0 | worn: percent of damage stopped (all worn armor adds up, capped at 60) |
| `recipe` | an object (station, item, count, ticks) |  | how colonists make it; needs a `use: "craft"` building and a bill |
| `recipe.station` | building id | required | the building it is made at |
| `recipe.item` | item id | required | the material used |
| `recipe.count` | a whole number | required | units of material per item |
| `recipe.ticks` | a whole number | 600 | work at normal speed (600 = 30 seconds); skill makes it faster |
| `keep` | a whole number | 0 | default bill: how many the colony keeps on hand (0 = make none until the player sets a bill) |
| `sprite` | sprite id (16px) |  | how it looks lying on the ground |
| `layer` | sprite id (16px) |  | apparel: drawn over the colonist on the map (16px, tinted by `color` through `$main`) |
| `portrait` | sprite id (32px) |  | apparel: drawn on the ID card portrait (32px). Legs need none |
| `hidesHair` | true or false | false | hats: the hair is not drawn under it |

## The game uses it automatically when...

- **Food**: any item with `nutrition` is eaten when colonists are hungry. Raw food is cooked at a
  building whose `product` is a meal.
- **Apparel**: colonists put on the best apparel lying around for the season by themselves: an empty
  slot first, then more `armor`, then `cold` when the days are cold and `heat` when they are hot. They
  take off a piece that makes them too hot.
- **Recipes**: an item with a `recipe` appears as a bill row at its station. Colonists make it while
  the colony has fewer than the bill (`keep` until the player changes it) and the material exists.
- **Materials**: an item is useful once something produces it: a plant's `harvestItem`/`woodItem`, a
  building's `mineItem` or `product`, an animal's `meatItem`/`leatherItem`, a recipe, or
  `startingItems` in `core.worldgen`. Otherwise it never exists.

## Example: core.item.tuque

```json
{
  "id": "core.item.tuque",
  "kind": "item",
  "label": "tuque",
  "color": "#b8423a",
  "stackLimit": 1,
  "slot": "head",
  "cold": 5,
  "heat": -2,
  "recipe": {"station": "core.building.tailor_bench", "item": "core.item.cloth", "count": 15, "ticks": 300},
  "keep": 0,
  "hidesHair": true,
  "sprite": "core.sprite.item.tuque",
  "layer": "core.sprite.wear.tuque",
  "portrait": "core.sprite.portrait.tuque"
}
```

## Gotchas

- Apparel without `layer` is an error; without `portrait` it is invisible on the ID card.
- `armor` over 60 does nothing more.
- An item no recipe, plant, building, animal or starting list produces never appears.
- You can reuse core sprites (the tuque's) while you draw your own; `color` still tints them.

---
<!-- file: docs/api/mod-json.md -->

# mod.json

Every mod has one, in its root folder. The game reads `loadAfter`; the rest is for players and tools.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | text |  | the mod id: one lowercase word, the same as the folder name and the first part of every id in the mod |
| `name` | text | "" | display name |
| `version` | text | "0.1.0" | your version, e.g. `"1.2.0"`: raise it when you publish a change |
| `authors` | a list of text |  | names |
| `description` | text | "" | one or two sentences for players |
| `modApi` | a whole number | 1 | the mod API version it was made for (`game.json` has the current one) |
| `loadAfter` | a list of text |  | mod ids to load before this one, when present (yours wins over theirs) |
| `requires` | a list of text |  | mod ids this one needs; the tools load them first when checking |

```json
{ "id": "furhats", "name": "Fur Hats", "version": "1.0.0", "authors": ["you"],
  "description": "Warm fur hats made from leather at the tailor bench.", "modApi": 1 }
```

## flags.json

A mod may also carry `flags.json`: `{ "name": true }`. Flags switch game features on and off; the
game only reads the flags it knows (`core.travel` today). A mod rarely needs one.

---
<!-- file: docs/api/plant.md -->

# plant

Wild plants, trees and crops. Plants grow from 0 to fully grown over `growTicks`, faster on fertile
ground and only in their temperature range and in daylight.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "plant" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb` |
| `glyph` | text | "grass" | how it is drawn when it has no sprite: `tree`, `cactus`, `bush`, `berry`, `crop`, anything else draws as grass |
| `growTicks` | a whole number | 30000 | ticks to grow fully at 100% fertility (6000 = one day) |
| `minTemp` | a whole number | 1 | coldest temperature it grows in |
| `maxTemp` | a whole number | 45 | hottest temperature it grows in |
| `tree` | true or false | false | chopped for wood instead of harvested; blocks walking less than walls |
| `woodYield` | a whole number | 0 | trees: wood from chopping a full-grown tree |
| `woodItem` | item id | "core.item.wood" | trees: what chopping gives |
| `harvestItem` | item id |  | what harvesting gives |
| `harvestYield` | a whole number | 0 | how much a full-grown plant gives |
| `harvestMin` | a whole number | 65 | percent grown before it can be harvested |
| `regrowTo` | a whole number | 0 | after harvest, regrows from this percent (0 = the plant is removed) |
| `sowable` | true or false | false | colonists can plant it in growing zones (appears in the grow-zone menu) |
| `minFertility` | a whole number | 50 | the ground's fertility it needs (soil is 100; sand and gravel less) |
| `pathCost` | a whole number | 100 | walking cost through it, percent (100 = no slower) |
| `spread` | a whole number | 0 | per mille chance per growth step to seed a neighbouring cell when grown |
| `workTicks` | a whole number | 60 | work to harvest, sow or chop at normal speed |
| `nutrition` | a whole number | 0 | what a grazing animal gets from eating a full-grown plant |
| `sprite` | sprite id (16px) |  | how it looks when well grown (16px); young plants are drawn by `glyph` |

## The game uses it automatically when...

- **Wild**: only if a biome lists it in its `plants` table. To add a wild plant to the tundra you
  must override `core.biome.tundra` (copy it whole and add `{"id": "mymod.plant.x", "weight": 10}`).
  New plants appear on maps generated after the mod loads, and spread on existing ones.
- **Crops**: `"sowable": true` puts it in the grow-zone menu. No biome needed.

## Example: core.plant.cotton

```json
{
  "id": "core.plant.cotton",
  "kind": "plant",
  "label": "cotton",
  "color": "#9fae7a",
  "glyph": "crop",
  "growTicks": 22000,
  "minTemp": 6,
  "sowable": true,
  "minFertility": 40,
  "harvestItem": "core.item.cloth",
  "harvestYield": 10,
  "harvestMin": 100,
  "workTicks": 50
}
```

---
<!-- file: docs/api/roof-and-rooms.md -->

# roof and core.rooms

Roofs cover rooms. Colonists roof enclosed rooms by themselves; rock comes with a natural roof.
A roofed room keeps out rain and most of the daily temperature swing.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "roof" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb` |
| `natural` | true or false | false | a mountain roof: generated over rock, stays when the rock is mined |
| `workTicks` | a whole number | 60 | work to build one cell |

## core.rooms (singleton)

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.rooms" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `autoRoofMax` | a whole number | 300 | colonists roof enclosed rooms up to this many cells |
| `indoorPercent` | a whole number | 75 | a room counts as indoors when this percent of it is roofed |
| `roofSupport` | a whole number | 6 | a built roof needs a wall or rock within this many cells or it collapses |
| `builtRoof` | roof id | "core.roof.built" | the roof colonists build |
| `rockRoof` | roof id | "core.roof.rock" | the roof generated over rock |

A new roof kind is only used if `core.rooms` names it.

---
<!-- file: docs/api/singletons.md -->

# Singletons

Defs the game reads by a fixed id. There is one of each. To change one, copy the whole def from
`reference/core/` into your mod and edit the copy: it replaces the original. Only one mod can do
this to each without conflicting.

## core.colonist: how colonists work

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.colonist" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `moveTicks` | a whole number | 6 | ticks per cell walked |
| `carryCapacity` | a whole number | 75 | units carried at once (hauling skill scales it) |
| `foodDecay` | a whole number | 7 | food need lost per need update |
| `restDecay` | a whole number | 6 | rest lost per need update |
| `bedRest` | a whole number | 30 | rest regained per update in a bed |
| `groundRest` | a whole number | 18 | rest regained per update on the ground |
| `eatTicks` | a whole number | 40 | time to eat |
| `maxHealth` | a whole number | 100 | base health (constitution adds or removes 5 per point from 10) |
| `damage` | a whole number | 11 | per shot |
| `attackTicks` | a whole number | 60 | ticks between shots |
| `range` | a whole number | 10 | shooting range in cells |
| `baseMood` | a whole number | 55 | mood with no thoughts, 0..100 |
| `minorBreak` | a whole number | 25 | below this mood a colonist may break down |
| `majorBreak` | a whole number | 10 | below this, more often |
| `comfortMin` | a whole number | 12 | coldest comfortable temperature (apparel widens it) |
| `comfortMax` | a whole number | 30 | hottest comfortable temperature |

## core.worldgen: the world and the landing party

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.worldgen" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `globeFrequency` | a whole number | 16 | globe detail: 10·F²+2 tiles (16 gives 2562) |
| `oceanPercent` | a whole number | 45 | share of the globe under water |
| `mapRadius` | a whole number | 64 | colony map radius in hex cells |
| `bandDepth` | a whole number | 7 | rows shared with each neighbouring map |
| `colonists` | a whole number | 3 | how many colonists land |
| `rockFloor` | terrain id | "core.terrain.rough_stone" | terrain under mined rock |
| `shallowWater` | terrain id | "core.terrain.shallow_water" | terrain for shallow water |
| `deepWater` | terrain id | "core.terrain.deep_water" | terrain for deep water |
| `marsh` | terrain id | "core.terrain.marsh" | terrain for marsh |
| `startingItems` | a list of objects |  | what the colonists bring |
| `startingItems[].item` | item id | required | the item |
| `startingItems[].count` | a whole number | required | how many |
| `startingApparel` | list of item ids |  | what each colonist wears at landing |

## core.names: colonist names

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.names" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `names` | a list of text | required | drawn without repeats; keep at least as many as `colonists` |

## core.rpg: attributes and skills

Colonists roll six attributes (3..18). A skill starts at the aptitude its attributes give and rises
with practice.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.rpg" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `attributes` | a list of objects |  | exactly six, keys `str dex con int wis cha`; change labels, colors, icons only |
| `attributes[].key` | text | required | fixed: the game reads attributes by these keys |
| `attributes[].label` | text | required | full name on the ID card |
| `attributes[].abbrev` | text | required | short name |
| `attributes[].color` | text | "#ffffff" | `#rrggbb` |
| `attributes[].icon` | sprite id (8px) |  | the card's icon |
| `skills` | an object of name: an object of name: a whole number |  | for each work type (`cook construct grow hunt mine plantcut craft haul`), attribute weights, e.g. `{"str": 2, "con": 1}` |
| `aptitudeMax` | a whole number | 8 | the highest starting skill an attribute mix gives |
| `levelCap` | a whole number | 20 | highest skill level |
| `xpBase` | a whole number | 1500 | practice for the first level up |
| `xpGrowth` | a whole number | 150 | extra practice per level |
| `intLearn` | a whole number | 6 | learning speed, percent per intelligence point over 10 |
| `conHealth` | a whole number | 5 | health per constitution point over 10 |
| `wisBreak` | a whole number | 1 | break threshold lowered per wisdom point over 10 |
| `chaRadius` | a whole number | 6 | cells within which charisma is felt |
| `chaHigh` | a whole number | 15 | charisma at or above this: nearby colonists feel "pleasant company" |
| `chaLow` | a whole number | 6 | at or below this: "grating company" |

## core.looks: what colonists look like

| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.looks" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `skins` | a list of text |  | skin colors, `#rrggbb` (`$skin` in sprites) |
| `hairs` | a list of text |  | hair colors (`$hair`) |
| `styles` | a list of objects |  | hair styles |
| `styles[].id` | text | required | a short name |
| `styles[].sprite` | sprite id (16px) | required | 16px hair drawn on the map |
| `styles[].portrait` | sprite id (32px) | required | 32px hair on the ID card |
| `minAge` | a whole number | 18 | youngest colonist |
| `maxAge` | a whole number | 60 | oldest |
| `body` | sprite id (16px) | "core.sprite.body" | the 16px body every colonist sprite starts from (with walking `frames`) |
| `head` | sprite id (32px) | "core.sprite.portrait.head" | the 32px head of the ID card portrait |

---
<!-- file: docs/api/sprite.md -->

# sprite

Pixel art, as text. Each row is a string; each character is one pixel, looked up in `palette`.
`.` is transparent. See `docs/art.md` for how to draw well at these sizes.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "sprite" |  | always this value |
| `size` | a whole number | 16 | 8 (attribute icons), 16 (anything on the map, worn layers, hair), 32 (ID card portraits) |
| `palette` | an object of name: text |  | character to color: `"#rrggbb"`, or a tint: `$main` (the item's or animal's `color`), `$skin`, `$hair`; add `-` for darker, `+` for lighter |
| `rows` | a list of text |  | exactly `size` strings of exactly `size` characters |
| `frames` | a list of a list of text |  | extra walking frames (body sprites only): each a list of rows like `rows` |

## Where sprites are used

| field | size |
| --- | --- |
| item `sprite`, apparel `layer`, building `sprite`, plant `sprite`, animal `sprite` | 16 |
| apparel `portrait`, `core.looks` `head` and hair `portrait` | 32 |
| `core.rpg` attribute `icon` | 8 |

A worn `layer` is drawn on top of the colonist's 16px body, so it must line up with
`core.sprite.body` (head at the top, feet at the bottom). A `portrait` is drawn over the 32px head
`core.sprite.portrait.head`. Preview with `python3 tools/modkit.py sprite ID --mod MYMOD`.

```json
{ "id": "mymod.sprite.item.gem", "kind": "sprite", "size": 16,
  "palette": { "k": "#1b1f24", "m": "$main", "M": "$main+", "d": "$main-" },
  "rows": [
    "................", "................", "................", "................",
    "......kkkk......", ".....kMMmmk.....", "....kMMmmmdk....", "....kMmmmmdk....",
    ".....kmmmdk.....", "......kmdk......", ".......kk.......", "................",
    "................", "................", "................", "................" ] }
```

---
<!-- file: docs/api/terrain.md -->

# terrain

The ground of each map cell.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "terrain" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb`; terrain is drawn as color only, it has no sprite |
| `pathCost` | a whole number | 100 | walking cost, percent (100 = normal) |
| `walkable` | true or false | true | false for deep water |
| `fertility` | a whole number | 0 | plant growth, percent (soil is 100; 0 = nothing grows) |
| `buildable` | true or false | true | blueprints can be placed on it |
| `water` | true or false | false | counts as water (not built on, drawn as water) |

## The game uses it automatically when...

A biome's `terrain` bands pick it (see `biome.md`), or `core.worldgen` names it as the rock floor,
shallow water, deep water or marsh. Then it appears on maps generated after the mod loads.

```json
{
  "id": "core.terrain.soil",
  "kind": "terrain",
  "label": "soil",
  "color": "#6b5537",
  "fertility": 100
}
```

---
<!-- file: docs/api/thought.md -->

# thought

Something a colonist feels: mood points while it lasts. **The game decides when each thought
happens**, in code: a mod can change how strong a built-in thought is and how long it lasts by
overriding its id, but a new thought id is never triggered (see `docs/limits.md`).

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "thought" |  | always this value |
| `label` | text | "" | shown on the colonist |
| `mood` | a whole number | 0 | mood points, plus or minus (mood runs 0..100 around a base of 55) |
| `ticks` | a whole number | 6000 | a memory lasts this long; a condition is held this long after it stops |

Built-in thoughts: `ate_meal ate_raw catharsis cold colonist_died exhausted freezing grating_company
hot hungry pain pleasant_company severe_pain slept_barracks slept_bedroom slept_cold slept_ground
slept_outside soaked starving sweltering tired` (all `core.thought.<name>`).

```json
{
  "id": "core.thought.cold",
  "kind": "thought",
  "label": "cold",
  "mood": -5,
  "ticks": 300
}
```

---
<!-- file: docs/api/weather.md -->

# weather

Picked at random, by weight, among the weathers allowed at the current temperature.

| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "weather" |  | always this value |
| `label` | text | "" | name shown in the game |
| `weight` | a whole number | 10 | relative chance |
| `minTemp` | a whole number | -100 | only when it is at least this warm |
| `maxTemp` | a whole number | 100 | only when it is at most this warm |
| `growth` | a whole number | 100 | plant growth while it lasts, percent |
| `tempOffset` | a whole number | 0 | degrees added outdoors |
| `minTicks` | a whole number | 1500 | shortest spell |
| `maxTicks` | a whole number | 6000 | longest spell |
| `wet` | true or false | false | soaks colonists outdoors (the "soaked" thought) |

New weathers join the draw automatically.

```json
{
  "id": "core.weather.rain",
  "kind": "weather",
  "label": "rain",
  "weight": 20,
  "minTemp": 1,
  "growth": 125,
  "tempOffset": -2,
  "wet": true
}
```

---
<!-- file: workflows/add-def.md -->

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

---
<!-- file: workflows/fix-validation-errors.md -->

# Workflow: fix validation errors

**Input:** the output of `python3 tools/modkit.py validate MODID`. **Output:** a clean run.

Each line is `SEVERITY file def field: message`. Work top to bottom; errors come first.

| message says | do this |
| --- | --- |
| `unknown field ... (did you mean 'x'?)` | rename the field to `x`. No suggestion: the field does not exist; remove it, or see `docs/limits.md` |
| `field names are case-sensitive: write "x"` | fix the capitalisation |
| `expected a whole number, found text "12"` | remove the quotes: `12` |
| `must be a whole number` | no decimals: `0.5` becomes a whole number in the field's unit |
| `no item 'x' (did you mean 'y'?)` | use `y`, or define `x` in the mod |
| `'x' is a plant, but this field needs a item` | point at a def of the right kind |
| `sprite 'x' is 16px; this field needs a 32px sprite` | use or draw a sprite of the right size |
| `has 15 rows` / `row 3 is 17 characters` | add or remove characters so the grid is exactly size × size |
| `row 2 uses 'q' not in the palette` | add `"q": "#rrggbb"` to the palette, or change the pixel |
| `no "kind"` / `unknown kind` | add the right `"kind"` |
| `id defined twice` | rename one |
| `missing required field` | add it (see the field table) |
| `will never appear` / `nothing makes this item` | connect it (biome table, recipe, harvestItem...) as the message says |
| `new ids should start with the mod id` | rename the id (and everything that points at it) |
| `overrides a def` (NOTE) | fine if intended: list it in NOTES.md "Overrides" |

Re-run validate after each batch of fixes. If the same error comes back twice, re-read the field
table in `docs/api/` for that kind instead of guessing.

*Done when:* `... 0 errors ... - OK`, and every remaining warning is fixed or explained in NOTES.md.

---
<!-- file: workflows/idea-to-spec.md -->

# Workflow: idea to spec

**Input:** an idea. **Output:** a spec in the mod's `NOTES.md` the person has agreed to.

1. Restate the idea in one or two sentences.
2. Map every part of the idea to a kind (`docs/concepts.md`). Check each against `docs/limits.md`.
   Parts that need a game update go under "Not possible yet" with the reason.
3. For each def decide: new (id `MODID.kind.name`) or an override of a core id (find it in
   `docs/ids.md`). Prefer new defs; override only when the idea is to change core.
4. Find the closest core def to copy for each new def (`reference/core/`).
5. Ask the person at most three questions, only where the answer changes what you build (for example
   "should the hat need leather or cloth?"). Offer a default for each.
6. Write the spec into NOTES.md:

```markdown
# <Mod name>
<one paragraph: what the player will notice>

## Defs
| id | kind | copy of | purpose |
| --- | --- | --- | --- |
| furhats.item.fur_hat | item | core.item.tuque | warm hat from leather |

## Overrides
| id | why |
| --- | --- |

## Not possible yet
- <part of the idea> — <limit from docs/limits.md>

## Numbers outside docs/balance.md
- <field = value> — <why>
```

*Done when:* the person says the spec is right (or, if you can't ask, it covers the whole idea).

---
<!-- file: workflows/make-sprite.md -->

# Workflow: make a sprite

**Input:** what to draw and where it is used. **Output:** a sprite def that validates and looks right.

1. Find the size from where it is used (`docs/api/sprite.md`): 16 for the map and worn layers, 32 for
   portraits, 8 for icons.
2. Copy the closest core sprite from `reference/core/sprites/` into `mods/MODID/defs/sprites.json`
   with id `MODID.sprite.<use>.<name>` (e.g. `furhats.sprite.wear.fur_hat`).
3. Change the rows following `docs/art.md`: dark outline `k`, `$main`/`$main-`/`$main+` for colored
   parts, light from the top left. Worn layers must line up with the body (hat rows 0..4).
4. Count: exactly `size` rows, each exactly `size` characters. Every character is `.` or a palette key.
5. Point the def at it (`sprite`, `layer` or `portrait`).
6. `python3 tools/modkit.py validate MODID`, then look:
   `python3 tools/modkit.py sprite MODID.sprite.<use>.<name> --mod MODID --main "#8a6a4a"`
   (use the item's `color` for `--main`). Without a terminal, add `--png out.png` and view the file.
7. Fix what looks wrong; two or three rounds is normal.

*Done when:* validate is clean and the preview reads as the thing at a glance.

---
<!-- file: workflows/new-mod.md -->

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
   and `{ "metric": "deaths", "max": 0 }` unless the mod is meant to be dangerous.
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

---
<!-- file: workflows/publish.md -->

# Workflow: publish

**Input:** a reviewed mod. **Output:** a zip to share.

1. `review.md` says APPROVE.
2. `mod.json`: `version` raised since the last release; `description` written for players.
3. `python3 tools/modkit.py pack MODID`. *Check:* it prints `wrote dist/MODID-VERSION.zip`.
4. Tell the person: the zip goes into the players' mods folder (`modkit doctor` shows where), and
   what to mention when sharing it (what it overrides, the game version).

---
<!-- file: workflows/review.md -->

# Workflow: review

**Input:** a mod. **Output:** `APPROVE` or `CHANGES:` with a numbered list. Use this on your own
work before reporting it done, and when asked to review someone else's mod.

Check each item. Write down every failure.

1. `python3 tools/modkit.py validate MODID` shows 0 errors.
2. Every warning is fixed or explained in NOTES.md.
3. Every new id starts with `MODID.` and says what it is (`furhats.item.fur_hat`, not `furhats.item.x1`).
4. Every override (the validator lists them) is in NOTES.md "Overrides" with a reason, and copies
   every field of the original that it doesn't mean to change (compare with `reference/core/`).
5. Numbers are within `docs/balance.md` ranges, or NOTES.md says why not.
6. Sprites: the right size for their use; outlined; `$main` where the def's color should show;
   worn layers line up with the body (preview them).
7. `tests/expect.json` has a `seen` check for every new item, plant, animal and building, and
   `modkit test` passes (or the game was not available, and that is said).
8. Nothing claims behaviour the game doesn't have (`docs/limits.md`): no fields that "should" do
   something, no new thoughts expected to trigger, no labels promising effects that aren't there.
9. `mod.json` has a name, version, description and `modApi` equal to `game.json`'s.
10. README.md tells a player what the mod adds and what it overrides.

Answer exactly:

```
APPROVE
```
or
```
CHANGES:
1. <file> <def>: <what is wrong> -> <what to do>
2. ...
```

---
<!-- file: workflows/test-and-balance.md -->

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

---
<!-- file: workflows/update-for-new-game-version.md -->

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

---
<!-- file: agents/artist.md -->

---
name: mod-artist
description: Draws pixel-art sprite defs for a WorldPulse mod (16px map sprites and worn layers, 32px portraits, 8px icons) and checks them. Use when a def needs its own art.
---

You are the pixel artist for a WorldPulse mod. Read `docs/art.md`, then follow
`workflows/make-sprite.md` for each sprite.

- Copy the closest core sprite from `reference/core/sprites/` and change it.
- Exactly `size` rows of exactly `size` characters; `.` is transparent.
- Dark outline `#1b1f24`; `$main`, `$main-`, `$main+` for the def's color; light from the top left.
- Worn layers line up with `core.sprite.body`; portraits with `core.sprite.portrait.head`.
- Preview every sprite (`python3 tools/modkit.py sprite ID --mod MODID --main "#hex"`) and fix what
  doesn't read at a glance.

Output: the sprite ids made, which def fields point at them, and the validate summary line.

---
<!-- file: agents/author.md -->

---
name: mod-author
description: Writes and fixes the JSON defs of a WorldPulse mod from its spec, validating after every change. Use after the spec exists.
---

You are the author of a WorldPulse mod. You write defs from the spec in the mod's NOTES.md.

Read `AGENTS.md`. For each def follow `workflows/add-def.md`; for validator output follow
`workflows/fix-validation-errors.md`.

- Use only fields from `docs/api/<kind>.md`. Never invent a field.
- Start every new def from a copy: `python3 tools/modkit.py new-def KIND NAME --like ID --mod MODID`.
- Run `python3 tools/modkit.py validate MODID` after every change; fix errors before moving on.
- Leave sprites pointing at core sprites; the artist replaces them.

Output: the list of defs written, and the final validate summary line.

---
<!-- file: agents/designer.md -->

---
name: mod-designer
description: Turns a WorldPulse mod idea into a concrete spec of defs in the mod's NOTES.md. Use at the start of a mod or when the idea changes.
---

You are the designer for a WorldPulse mod. You turn an idea into a spec; you do not write defs.

Read `AGENTS.md`, `docs/concepts.md` and `docs/limits.md` first. Then follow
`workflows/idea-to-spec.md` exactly.

- Every part of the idea becomes a def of an existing kind, an override of a core def, or a line
  under "Not possible yet" with the reason from `docs/limits.md`.
- Name the core def each new def should be copied from (look in `reference/core/` and `docs/ids.md`).
- Ask at most three questions, each with a default answer.
- Keep the mod small: the fewest defs that deliver the idea.

Output: the spec written into the mod's NOTES.md, and a three-line summary.

---
<!-- file: agents/reviewer.md -->

---
name: mod-reviewer
description: Reviews a WorldPulse mod against the fixed checklist and answers APPROVE or CHANGES with a numbered list. Use before reporting a mod done or publishing it.
---

You are the reviewer for a WorldPulse mod. You do not edit files. Follow `workflows/review.md`:
check all ten items, running the commands it names. Be specific: name the file, def and field, what
is wrong, and what to do.

Answer only with `APPROVE`, or `CHANGES:` and a numbered list, in the format the workflow gives.

---
<!-- file: agents/tester.md -->

---
name: mod-tester
description: Runs a WorldPulse mod's tests (modkit validate and test with tests/expect.json), reads the simulation report and says what is wrong. Use before review and after balance changes.
---

You are the tester for a WorldPulse mod. Follow `workflows/test-and-balance.md`.

- Write or update `tests/expect.json` (`docs/testing.md`): a `seen` check per new item, plant,
  animal and building; deaths, breaks or mood limits that match the mod's intent.
- Run `python3 tools/modkit.py test MODID`. If the game is not found, say so and run `validate` only.
- For every `NEVER` def, find the cause (not listed in a biome, wrong climate, no material, no cost).
- Compare numbers with `docs/balance.md`.

Output, exactly:

```
TEST <passed | failed | not run (game not found)>
- <finding> -> <suggested fix>
```

---
<!-- file: docs/ids.md -->

# Core ids

Every id in the game's core content, by kind, for reference and reuse (point at core sprites,
materials and stations freely). Regenerated by `modkit bundle`.

- **animal**: `core.animal.bear`, `core.animal.boar`, `core.animal.capybara`, `core.animal.cougar`, `core.animal.deer`, `core.animal.elk`, `core.animal.hare`, `core.animal.ibex`, `core.animal.wolf`
- **biome**: `core.biome.arid_shrubland`, `core.biome.boreal_forest`, `core.biome.desert`, `core.biome.ice_sheet`, `core.biome.ocean`, `core.biome.sea_ice`, `core.biome.swamp`, `core.biome.temperate_forest`, `core.biome.temperate_grassland`, `core.biome.tropical_rainforest`, `core.biome.tundra`
- **building**: `core.building.bed`, `core.building.campfire`, `core.building.cooler`, `core.building.door`, `core.building.fireplace`, `core.building.granite`, `core.building.limestone`, `core.building.marble`, `core.building.sandstone`, `core.building.steel_ore`, `core.building.tailor_bench`, `core.building.wall_stone`, `core.building.wall_wood`
- **item**: `core.item.berries`, `core.item.cloth`, `core.item.leather`, `core.item.leather_vest`, `core.item.meal`, `core.item.meat`, `core.item.parka`, `core.item.potato`, `core.item.rice`, `core.item.steel`, `core.item.stone`, `core.item.sun_hat`, `core.item.trousers`, `core.item.tunic`, `core.item.tuque`, `core.item.wood`
- **plant**: `core.plant.berry_bush`, `core.plant.bush`, `core.plant.cactus`, `core.plant.cotton`, `core.plant.grass`, `core.plant.oak`, `core.plant.pine`, `core.plant.poplar`, `core.plant.potato`, `core.plant.rice`, `core.plant.tall_grass`, `core.plant.teak`
- **roof**: `core.roof.built`, `core.roof.rock`
- **sprite**: `core.sprite.animal.bear`, `core.sprite.animal.boar`, `core.sprite.animal.canine`, `core.sprite.animal.deer`, `core.sprite.animal.feline`, `core.sprite.animal.small`, `core.sprite.body`, `core.sprite.building.bed`, `core.sprite.building.campfire`, `core.sprite.building.cooler`, `core.sprite.building.door`, `core.sprite.building.fireplace`, `core.sprite.building.tailor_bench`, `core.sprite.hair.bun`, `core.sprite.hair.long`, `core.sprite.hair.shaved`, `core.sprite.hair.short`, `core.sprite.icon.cha`, `core.sprite.icon.con`, `core.sprite.icon.dex`, `core.sprite.icon.int`, `core.sprite.icon.str`, `core.sprite.icon.wis`, `core.sprite.item.berries`, `core.sprite.item.cloth`, `core.sprite.item.leather`, `core.sprite.item.leather_vest`, `core.sprite.item.meal`, `core.sprite.item.meat`, `core.sprite.item.parka`, `core.sprite.item.potato`, `core.sprite.item.rice`, `core.sprite.item.steel`, `core.sprite.item.stone`, `core.sprite.item.sun_hat`, `core.sprite.item.trousers`, `core.sprite.item.tunic`, `core.sprite.item.tuque`, `core.sprite.item.wood`, `core.sprite.portrait.hair.bun`, `core.sprite.portrait.hair.long`, `core.sprite.portrait.hair.shaved`, `core.sprite.portrait.hair.short`, `core.sprite.portrait.head`, `core.sprite.portrait.leather_vest`, `core.sprite.portrait.parka`, `core.sprite.portrait.sun_hat`, `core.sprite.portrait.tunic`, `core.sprite.portrait.tuque`, `core.sprite.tree.broadleaf`, `core.sprite.tree.pine`, `core.sprite.wear.leather_vest`, `core.sprite.wear.parka`, `core.sprite.wear.sun_hat`, `core.sprite.wear.trousers`, `core.sprite.wear.tunic`, `core.sprite.wear.tuque`
- **terrain**: `core.terrain.deep_water`, `core.terrain.gravel`, `core.terrain.ice`, `core.terrain.marsh`, `core.terrain.rich_soil`, `core.terrain.rough_stone`, `core.terrain.sand`, `core.terrain.shallow_water`, `core.terrain.soil`
- **thought**: `core.thought.ate_meal`, `core.thought.ate_raw`, `core.thought.catharsis`, `core.thought.cold`, `core.thought.colonist_died`, `core.thought.exhausted`, `core.thought.freezing`, `core.thought.grating_company`, `core.thought.hot`, `core.thought.hungry`, `core.thought.pain`, `core.thought.pleasant_company`, `core.thought.severe_pain`, `core.thought.slept_barracks`, `core.thought.slept_bedroom`, `core.thought.slept_cold`, `core.thought.slept_ground`, `core.thought.slept_outside`, `core.thought.soaked`, `core.thought.starving`, `core.thought.sweltering`, `core.thought.tired`
- **weather**: `core.weather.clear`, `core.weather.cloudy`, `core.weather.fog`, `core.weather.rain`, `core.weather.snow`, `core.weather.storm`
- **singletons**: `core.colonist`, `core.looks`, `core.names`, `core.rooms`, `core.rpg`, `core.worldgen`

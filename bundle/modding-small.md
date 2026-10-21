# WorldPulse modding (small)

Everything an AI assistant needs to write WorldPulse mods, in one file. Game: mod API 1, core content e5a94f1feb3c.
Paste or attach this file, then describe the mod you want. Follow the rules in AGENTS.md exactly.
This is the short version for small models; modding-full.md has everything.

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

`biome` lands every seed in that biome, for mods about one place (the test makes that biome the best
landing site in its own copy of the content; your mod is not changed).
`days`, `seeds` and `biome` can be overridden: `modkit test furhats --days 3 --seeds 1`.

## Layer 3: play it

`python3 tools/modkit.py install furhats` copies the mod into the game's mods folder and reloads a
running game; `restore`/`uninstall` undo it. Sprites, the ID card and how it *feels* are only
checked by playing.

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

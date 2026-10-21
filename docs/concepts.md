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

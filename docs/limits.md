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

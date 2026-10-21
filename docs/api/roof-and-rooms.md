# roof and core.rooms

Roofs cover rooms. Colonists roof enclosed rooms by themselves; rock comes with a natural roof.
A roofed room keeps out rain and most of the daily temperature swing.

<!-- fields:roof -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "roof" |  | always this value |
| `label` | text | "" | name shown in the game |
| `color` | text | "#ff00ff" | `#rrggbb` |
| `natural` | true or false | false | a mountain roof: generated over rock, stays when the rock is mined |
| `workTicks` | a whole number | 60 | work to build one cell |
<!-- /fields -->

## core.rooms (singleton)

<!-- fields:core.rooms -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.rooms" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `autoRoofMax` | a whole number | 300 | colonists roof enclosed rooms up to this many cells |
| `indoorPercent` | a whole number | 75 | a room counts as indoors when this percent of it is roofed |
| `roofSupport` | a whole number | 6 | a built roof needs a wall or rock within this many cells or it collapses |
| `builtRoof` | roof id | "core.roof.built" | the roof colonists build |
| `rockRoof` | roof id | "core.roof.rock" | the roof generated over rock |
<!-- /fields -->

A new roof kind is only used if `core.rooms` names it.

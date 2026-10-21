# terrain

The ground of each map cell.

<!-- fields:terrain -->
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
<!-- /fields -->

## The game uses it automatically when...

A biome's `terrain` bands pick it (see `biome.md`), or `core.worldgen` names it as the rock floor,
shallow water, deep water or marsh. Then it appears on maps generated after the mod loads.

<!-- generated:example:core.terrain.soil -->
```json
{
  "id": "core.terrain.soil",
  "kind": "terrain",
  "label": "soil",
  "color": "#6b5537",
  "fertility": 100
}
```
<!-- /generated -->

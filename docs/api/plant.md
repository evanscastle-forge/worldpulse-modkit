# plant

Wild plants, trees and crops. Plants grow from 0 to fully grown over `growTicks`, faster on fertile
ground and only in their temperature range and in daylight.

<!-- fields:plant -->
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
<!-- /fields -->

## The game uses it automatically when...

- **Wild**: only if a biome lists it in its `plants` table. To add a wild plant to the tundra you
  must override `core.biome.tundra` (copy it whole and add `{"id": "mymod.plant.x", "weight": 10}`).
  New plants appear on maps generated after the mod loads, and spread on existing ones.
- **Crops**: `"sowable": true` puts it in the grow-zone menu. No biome needed.

## Example: core.plant.cotton

<!-- generated:example:core.plant.cotton -->
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
<!-- /generated -->

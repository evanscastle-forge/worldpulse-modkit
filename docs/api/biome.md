# biome

What a tile of the globe is like, and what its colony maps are made of. The globe is generated
once per game: a new or changed biome only shows on new games, and on maps first visited after the
mod loads.

<!-- fields:biome -->
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
<!-- /fields -->

## Adding a plant or animal to an existing biome

There is no "append": copy the whole biome def into your mod, keep every field, and add your entry
to `plants` or `animals`. Your copy replaces the core one. Two mods that both do this to the same
biome conflict; see `docs/compatibility.md`.

<!-- generated:example:core.biome.tundra -->
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
<!-- /generated -->

# animal

Wild animals. Grazers eat plants; predators hunt smaller animals and, when starving, sometimes
colonists. Hunted, they leave meat and leather.

<!-- fields:animal -->
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
<!-- /fields -->

## The game uses it automatically when...

Only if a biome lists it in its `animals` table: on new maps at generation, and in arrivals from the
map edge over time. To add an animal to the boreal forest, override `core.biome.boreal_forest`
(copy it whole) and add `{"id": "mymod.animal.x", "weight": 10}` to its `animals`.

## Example: core.animal.wolf

<!-- generated:example:core.animal.wolf -->
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
<!-- /generated -->

## Gotchas

- A dangerous predator (high `damage`, `manhuntChance`) can kill a colony. Run `modkit test` and
  check deaths.

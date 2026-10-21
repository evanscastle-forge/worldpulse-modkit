# item

Things that lie on the ground in stacks, get carried, eaten, worn and used as building material.
Food, materials (wood, stone, cloth, leather) and **apparel** are all items.

<!-- fields:item -->
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
<!-- /fields -->

## The game uses it automatically when...

- **Food**: any item with `nutrition` is eaten when colonists are hungry. Raw food is cooked at a
  building whose `product` is a meal.
- **Apparel**: colonists put on the best apparel lying around for the season by themselves. Each
  piece scores `1 + armor`, plus `2 × cold` when the day's mean temperature is below `comfortMin + 5`
  (17° with core's `core.colonist`), plus `2 × heat` when it is above `comfortMax − 5` (25°). In each
  slot they wear the highest score (an empty slot scores 0) and take off a piece that scores below 0. So in winter a warm piece (cold 20 scores
  41 + armor) beats an armored one (the vest: 1 + 25 + 8 = 34), and in summer armor wins unless the
  piece has negative `heat`.
- **Recipes**: an item with a `recipe` appears as a bill row at its station. Colonists make it while
  the colony has fewer than the bill (`keep` until the player changes it) and the material exists.
- **Materials**: an item is useful once something produces it: a plant's `harvestItem`/`woodItem`, a
  building's `mineItem` or `product`, an animal's `meatItem`/`leatherItem`, a recipe, or
  `startingItems` in `core.worldgen`. Otherwise it never exists.

## Example: core.item.tuque

<!-- generated:example:core.item.tuque -->
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
<!-- /generated -->

## Gotchas

- Apparel without `layer` is an error; without `portrait` it is invisible on the ID card.
- `armor` over 60 does nothing more.
- An item no recipe, plant, building, animal or starting list produces never appears.
- You can reuse core sprites (the tuque's) while you draw your own; `color` still tints them.

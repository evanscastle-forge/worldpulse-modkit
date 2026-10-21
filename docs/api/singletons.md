# Singletons

Defs the game reads by a fixed id. There is one of each. To change one, copy the whole def from
`reference/core/` into your mod and edit the copy: it replaces the original. Only one mod can do
this to each without conflicting.

## core.colonist: how colonists work

<!-- fields:core.colonist -->
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
<!-- /fields -->

## core.worldgen: the world and the landing party

<!-- fields:core.worldgen -->
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
<!-- /fields -->

## core.names: colonist names

<!-- fields:core.names -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | "core.names" |  | always this value |
| `kind` | text |  | optional; the game finds this def by its id |
| `names` | a list of text | required | drawn without repeats; keep at least as many as `colonists` |
<!-- /fields -->

## core.rpg: attributes and skills

Colonists roll six attributes (3..18). A skill starts at the aptitude its attributes give and rises
with practice.

<!-- fields:core.rpg -->
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
<!-- /fields -->

## core.looks: what colonists look like

<!-- fields:core.looks -->
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
<!-- /fields -->

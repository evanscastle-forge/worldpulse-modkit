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

<!-- generated:balance -->
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
<!-- /generated -->

# Tundra Wolves

Packs of pale arctic wolves roam the tundra: smaller and less dangerous than the grey wolf, but
there are more of them, and their hides are worth taking.

## Defs
| id | kind | copy of | purpose |
| --- | --- | --- | --- |
| tundrawolves.animal.arctic_wolf | animal | core.animal.wolf | predator of the cold: health 60, damage 8, manhunt 3%, lives from -50 to 5 degrees; drawn with the core canine sprite tinted white |

## Overrides
| id | why |
| --- | --- |
| core.biome.tundra | adds the arctic wolf to its `animals` (weight 20); every other field is core's. Conflicts with other mods that override the tundra |

## Not possible yet
- Wolves hunting in packs (moving together) is animal behaviour, which needs the game.

## Numbers outside docs/balance.md
- None.

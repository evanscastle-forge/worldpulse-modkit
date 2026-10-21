# Workflow: make a sprite

**Input:** what to draw and where it is used. **Output:** a sprite def that validates and looks right.

1. Find the size from where it is used (`docs/api/sprite.md`): 16 for the map and worn layers, 32 for
   portraits, 8 for icons.
2. Copy the closest core sprite from `reference/core/sprites/` into `mods/MODID/defs/sprites.json`
   with id `MODID.sprite.<use>.<name>` (e.g. `furhats.sprite.wear.fur_hat`).
3. Change the rows following `docs/art.md`: dark outline `k`, `$main`/`$main-`/`$main+` for colored
   parts, light from the top left. Worn layers must line up with the body (hat rows 0..4).
4. Count: exactly `size` rows, each exactly `size` characters. Every character is `.` or a palette key.
5. Point the def at it (`sprite`, `layer` or `portrait`).
6. `python3 tools/modkit.py validate MODID`, then look:
   `python3 tools/modkit.py sprite MODID.sprite.<use>.<name> --mod MODID --main "#8a6a4a"`
   (use the item's `color` for `--main`). Without a terminal, add `--png out.png` and view the file.
7. Fix what looks wrong; two or three rounds is normal.

*Done when:* validate is clean and the preview reads as the thing at a glance.

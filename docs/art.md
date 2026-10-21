# Pixel art

WorldPulse's art is tiny pixel sprites stored as text in sprite defs (`docs/api/sprite.md`). An
assistant can draw them, and `python3 tools/modkit.py sprite ID --mod MYMOD` shows the result in the
terminal (or `--png out.png` for a picture to look at or paste into a chat).

## The house style

- **A dark outline** `#1b1f24` (palette key `k`) around every shape. It is what makes things
  readable on any ground.
- **Few colors**: a main color, a darker shade for the bottom/shadow side, a lighter one for the
  top-left highlight. Light comes from the top left.
- **Use tints, not fixed colors**, for anything that should take the def's color: `$main`, `$main-`
  (darker), `$main+` (lighter). One sprite then serves many items or animals (all core animals
  share six silhouettes).
- **Sizes**: 16×16 for anything on the map, 32×32 for ID-card portraits, 8×8 for attribute icons.
  At 16px a hat is 4 rows tall; don't try to draw details smaller than 2 pixels.
- Leave transparent space (`.`) around a thing on the ground: items sit in the middle of their cell.

## Worn apparel must line up with the body

A worn `layer` is drawn on top of the 16px body below, so hats cover rows 0..4, tops rows 8..12,
legs rows 12..15. Draw the layer with the body in mind and leave every other pixel `.`.

```
core.sprite.body                 core.sprite.wear.tuque (a hat layer)
................  row 0          .......ll.......
.....kkkkkk.....                 ....kmmmmmmk....
....kssssssk....                 ....kmmmmmmk....
....kssssssk....                 ....kMMMMMMk....
....kskssksk....  eyes           ................
....kssssssk....                 ................
....kSssssSk....                 ................
.....kkSSkk.....                 ................
....kuuuuuuk....  row 8: shirt   ................
...ksuuuuuusk...                 ................
...ksuuuuuusk...                 ................
...kskuuuuksk...                 ................
....kddddddk....  row 12: legs   ................
....kddkkddk....                 ................
....kSSkkSSk....                 ................
....kffkkffk....  row 15: feet   ................
```

Body palette: `k` outline, `s` `$skin`, `S` `$skin-`, `u` undershirt, `d` trousers, `f` feet. The
32px portrait is a head and shoulders: hats sit on rows 0..12 of the portrait; look at
`core.sprite.portrait.tuque` and `core.sprite.portrait.head` in `reference/core/sprites/`.

## A worked example: a fur hat

```json
{ "id": "furhats.sprite.wear.fur_hat", "kind": "sprite", "size": 16,
  "palette": { "k": "#1b1f24", "m": "$main", "M": "$main-", "l": "$main+", "w": "#e9e2d0" },
  "rows": [
    "....kwwwwwwk....",
    "...kwlmmmmlwk...",
    "...kmmmmmmmmk...",
    "...kwMMMMMMwk...",
    "................", "................", "................", "................",
    "................", "................", "................", "................",
    "................", "................", "................", "................" ] }
```

Check it: every row is 16 characters, every character is in the palette or `.`, and the preview
looks like a hat on a head (`modkit sprite furhats.sprite.wear.fur_hat --mod furhats`).

## Drawing tips for assistants

1. Start from the closest core sprite (`reference/core/sprites/`), copy it, and change it. That
   keeps the size, outline and alignment right.
2. Write the rows, then count: exactly `size` rows of exactly `size` characters.
3. Preview, look, adjust. Two or three rounds is normal.

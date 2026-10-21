# sprite

Pixel art, as text. Each row is a string; each character is one pixel, looked up in `palette`.
`.` is transparent. See `docs/art.md` for how to draw well at these sizes.

<!-- fields:sprite -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "sprite" |  | always this value |
| `size` | a whole number | 16 | 8 (attribute icons), 16 (anything on the map, worn layers, hair), 32 (ID card portraits) |
| `palette` | an object of name: text |  | character to color: `"#rrggbb"`, or a tint: `$main` (the item's or animal's `color`), `$skin`, `$hair`; add `-` for darker, `+` for lighter |
| `rows` | a list of text |  | exactly `size` strings of exactly `size` characters |
| `frames` | a list of a list of text |  | extra walking frames (body sprites only): each a list of rows like `rows` |
<!-- /fields -->

## Where sprites are used

| field | size |
| --- | --- |
| item `sprite`, apparel `layer`, building `sprite`, plant `sprite`, animal `sprite` | 16 |
| apparel `portrait`, `core.looks` `head` and hair `portrait` | 32 |
| `core.rpg` attribute `icon` | 8 |

A worn `layer` is drawn on top of the colonist's 16px body, so it must line up with
`core.sprite.body` (head at the top, feet at the bottom). A `portrait` is drawn over the 32px head
`core.sprite.portrait.head`. Preview with `python3 tools/modkit.py sprite ID --mod MYMOD`.

```json
{ "id": "mymod.sprite.item.gem", "kind": "sprite", "size": 16,
  "palette": { "k": "#1b1f24", "m": "$main", "M": "$main+", "d": "$main-" },
  "rows": [
    "................", "................", "................", "................",
    "......kkkk......", ".....kMMmmk.....", "....kMMmmmdk....", "....kMmmmmdk....",
    ".....kmmmdk.....", "......kmdk......", ".......kk.......", "................",
    "................", "................", "................", "................" ] }
```

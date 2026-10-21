# Workflow: fix validation errors

**Input:** the output of `python3 tools/modkit.py validate MODID`. **Output:** a clean run.

Each line is `SEVERITY file def field: message`. Work top to bottom; errors come first.

| message says | do this |
| --- | --- |
| `unknown field ... (did you mean 'x'?)` | rename the field to `x`. No suggestion: the field does not exist; remove it, or see `docs/limits.md` |
| `field names are case-sensitive: write "x"` | fix the capitalisation |
| `expected a whole number, found text "12"` | remove the quotes: `12` |
| `must be a whole number` | no decimals: `0.5` becomes a whole number in the field's unit |
| `no item 'x' (did you mean 'y'?)` | use `y`, or define `x` in the mod |
| `'x' is a plant, but this field needs a item` | point at a def of the right kind |
| `sprite 'x' is 16px; this field needs a 32px sprite` | use or draw a sprite of the right size |
| `has 15 rows` / `row 3 is 17 characters` | add or remove characters so the grid is exactly size × size |
| `row 2 uses 'q' not in the palette` | add `"q": "#rrggbb"` to the palette, or change the pixel |
| `no "kind"` / `unknown kind` | add the right `"kind"` |
| `id defined twice` | rename one |
| `missing required field` | add it (see the field table) |
| `will never appear` / `nothing makes this item` | connect it (biome table, recipe, harvestItem...) as the message says |
| `new ids should start with the mod id` | rename the id (and everything that points at it) |
| `overrides a def` (NOTE) | fine if intended: list it in NOTES.md "Overrides" |

Re-run validate after each batch of fixes. If the same error comes back twice, re-read the field
table in `docs/api/` for that kind instead of guessing.

*Done when:* `... 0 errors ... - OK`, and every remaining warning is fixed or explained in NOTES.md.

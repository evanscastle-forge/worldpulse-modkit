# mod.json

Every mod has one, in its root folder. The game reads `loadAfter`; the rest is for players and tools.

<!-- fields:mod -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `id` | text |  | the mod id: one lowercase word, the same as the folder name and the first part of every id in the mod |
| `name` | text | "" | display name |
| `version` | text | "0.1.0" | your version, e.g. `"1.2.0"`: raise it when you publish a change |
| `authors` | a list of text |  | names |
| `description` | text | "" | one or two sentences for players |
| `modApi` | a whole number | 1 | the mod API version it was made for (`game.json` has the current one) |
| `loadAfter` | a list of text |  | mod ids to load before this one, when present (yours wins over theirs) |
| `requires` | a list of text |  | mod ids this one needs; the tools load them first when checking |
<!-- /fields -->

```json
{ "id": "furhats", "name": "Fur Hats", "version": "1.0.0", "authors": ["you"],
  "description": "Warm fur hats made from leather at the tailor bench.", "modApi": 1 }
```

## flags.json

A mod may also carry `flags.json`: `{ "name": true }`. Flags switch game features on and off; the
game only reads the flags it knows (`core.travel` today). A mod rarely needs one.

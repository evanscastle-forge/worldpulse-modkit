# thought

Something a colonist feels: mood points while it lasts. **The game decides when each thought
happens**, in code: a mod can change how strong a built-in thought is and how long it lasts by
overriding its id, but a new thought id is never triggered (see `docs/limits.md`).

<!-- fields:thought -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "thought" |  | always this value |
| `label` | text | "" | shown on the colonist |
| `mood` | a whole number | 0 | mood points, plus or minus (mood runs 0..100 around a base of 55) |
| `ticks` | a whole number | 6000 | a memory lasts this long; a condition is held this long after it stops |
<!-- /fields -->

Built-in thoughts: `ate_meal ate_raw catharsis cold colonist_died exhausted freezing grating_company
hot hungry pain pleasant_company severe_pain slept_barracks slept_bedroom slept_cold slept_ground
slept_outside soaked starving sweltering tired` (all `core.thought.<name>`).

<!-- generated:example:core.thought.cold -->
```json
{
  "id": "core.thought.cold",
  "kind": "thought",
  "label": "cold",
  "mood": -5,
  "ticks": 300
}
```
<!-- /generated -->

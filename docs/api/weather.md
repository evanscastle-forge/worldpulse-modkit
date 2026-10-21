# weather

Picked at random, by weight, among the weathers allowed at the current temperature.

<!-- fields:weather -->
| field | type | default | meaning |
| --- | --- | --- | --- |
| `kind` | "weather" |  | always this value |
| `label` | text | "" | name shown in the game |
| `weight` | a whole number | 10 | relative chance |
| `minTemp` | a whole number | -100 | only when it is at least this warm |
| `maxTemp` | a whole number | 100 | only when it is at most this warm |
| `growth` | a whole number | 100 | plant growth while it lasts, percent |
| `tempOffset` | a whole number | 0 | degrees added outdoors |
| `minTicks` | a whole number | 1500 | shortest spell |
| `maxTicks` | a whole number | 6000 | longest spell |
| `wet` | true or false | false | soaks colonists outdoors (the "soaked" thought) |
<!-- /fields -->

New weathers join the draw automatically.

<!-- generated:example:core.weather.rain -->
```json
{
  "id": "core.weather.rain",
  "kind": "weather",
  "label": "rain",
  "weight": 20,
  "minTemp": 1,
  "growth": 125,
  "tempOffset": -2,
  "wet": true
}
```
<!-- /generated -->

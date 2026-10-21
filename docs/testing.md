# Testing a mod

Two layers. Run the first after every change; run the second before you call the mod done.

## Layer 1: `modkit validate` (no game needed)

```
python3 tools/modkit.py validate furhats
```

Checks against the schemas and the core content in this toolkit: unknown or misspelled fields, wrong
value types, ids that don't exist (with a "did you mean"), the wrong kind or sprite size, sprite grids,
apparel without a worn layer, and things the game will never use (an animal no biome lists, an item
nothing makes, a new thought). Every message says how to fix it. Errors must be fixed; warnings
should be fixed or explained in NOTES.md; notes are information.

If the game is installed and found (`modkit doctor`), `validate` also runs the game's own check.

## Layer 2: `modkit test` (needs the game)

```
python3 tools/modkit.py test furhats
```

Runs the game's `modtool validate`, then `modtool simulate`: the game plays your mod in an
unattended colony for some days on a few seeds, and reports

- whether each of your defs **showed up** (an item existed, a plant grew, an animal appeared, a
  building was built, a thought was felt), the most at once, and the first day;
- deaths, breakdowns and mood, so you can see if you made the game too hard or too easy;
- crashes, if any.

Simulate watches only your mod's own defs (an overridden core def counts as yours: a biome override
is "seen" when the colony lands in it). It cannot tell you that bears became more common; play for that.

After landing, the simulated colony is given a starter setup for your mod: your buildings and the
stations of your recipes are placed, your recipes get bills of 2, your sowable plants get growing
zones, and your animals are hunted when they appear. A recipe's material is supplied the way a player
would: timid grazers that drop it are hunted, crops that yield it are sown. Nothing else is done for it.

### tests/expect.json

What must hold for the mod to pass. `modkit test` (and the game) read it.

```json
{
  "days": 10,
  "seeds": [1, 2, 3],
  "biome": "core.biome.tundra",
  "expect": [
    { "metric": "seen", "id": "furhats.item.fur_hat", "min": 2 },
    { "metric": "deaths", "max": 0 },
    { "metric": "moodAvg", "min": 40 }
  ]
}
```

| metric | value | default check |
| --- | --- | --- |
| `seen` (needs `id`) | how many seeds it showed up in | at least 1 |
| `peak` (needs `id`) | the most of it at once, best seed | at least 1 |
| `deaths` | colonist deaths, worst seed | |
| `alive` | colonists alive at the end, worst seed | |
| `breaks` | breakdowns, worst seed | |
| `moodAvg` | average mood, worst seed | |
| `moodMin` | lowest mood, worst seed | |

`biome` lands every seed in that biome, for mods about one place (the test makes that biome the best
landing site in its own copy of the content; your mod is not changed).
`days`, `seeds` and `biome` can be overridden: `modkit test furhats --days 3 --seeds 1`.

## Layer 3: play it

`python3 tools/modkit.py install furhats` copies the mod into the game's mods folder and reloads a
running game; `restore`/`uninstall` undo it. Sprites, the ID card and how it *feels* are only
checked by playing.

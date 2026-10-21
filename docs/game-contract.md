# What the toolkit expects from the game

The toolkit is public; the game is not. This page is the contract between them, versioned by the
**mod API version** (`modApi` in `game.json`). When the game changes something here, it bumps
`modApi` and this toolkit is updated with `game.json`, `schemas/` and `reference/core/` exported from
that game build.

## The game's mod tool

The game ships a headless tool (`Headless.dll`, run with `dotnet`, or a native executable) with:

| command | output | exit code |
| --- | --- | --- |
| `modtool version [--json]` | `{modApi, saveVersion, coreHash, ticksPerSecond, ticksPerDay, kinds, singletons, workTypes, apparelSlots}` | 0 |
| `modtool validate MOD_DIR [--json]` | issues: `{severity: error\|warning\|note, message, file, def, field}`, plus `modId`, `defs`, `overrides` | 0 ok, 1 errors |
| `modtool simulate MOD_DIR [--days N] [--seeds a,b] [--biome ID] [--json]` | per seed: biome, alive, deaths, breaks, moodAvg, moodMin, defs `{id: {kind, seen, peak, firstTick}}`, notable lines, failure; expectations from `tests/expect.json` | 0 ok, 1 failed |
| `modtool schema --out DIR` | JSON Schemas: `<kind>.schema.json`, `<singleton id>.schema.json`, `mod.schema.json` | 0 |
| `modtool export --out DIR` | refreshes a toolkit checkout: `schemas/`, `reference/core/`, `game.json` | 0 |
| `ctl reload` | reloads mods in the running game | 0, or 1 if no game is running |

Schema extensions: `x-ref` (the field holds an id of that kind), `x-size` (sprite size the field
needs), `x-nullable`, `x-known` (values with behaviour; others allowed but inert), `x-modApi`.

## Loading rules the toolkit relies on

- Mods live in `<data>/mods/<id>/` (`<data>`: `%LOCALAPPDATA%\WorldPulse`, `~/Library/Application
  Support/WorldPulse`, `$XDG_DATA_HOME/worldpulse` or `~/.local/share/worldpulse`; `WORLDPULSE_DATA`
  overrides). They load after core: by `load-order.txt`, else by name after their `loadAfter`.
- Every `*.json` in a mod is content except the root `mod.json`, `flags.json` and `tests/`.
- Same id = whole replacement. Unknown fields are ignored. Missing fields take defaults.

## Requested from the game (not available yet)

1. **Panel mod mode**: the agent panel works on a mod folder with a player-chosen agent command
   (this toolkit's `panel_adapter.py` or any agent speaking `docs/panel-protocol.md`), mapping
   `yes`/`back`/`keep` to `modkit install`/`restore`/an expectation.
2. **List-append patches**: a def kind that adds entries to another def's list (a biome's `plants` or
   `animals`) without replacing it, so mods stop conflicting over biomes.
3. **Data-driven thought triggers** (e.g. "near a building of def X", "wearing item X").
4. **More building uses** with behaviour (`well`, `table`, `research`).
5. **Scripting**: a sandboxed, deterministic scripting layer running inside the game tick.
6. **Loader warnings for unknown fields**, so players see what `modkit validate` sees.

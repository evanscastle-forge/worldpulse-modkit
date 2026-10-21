# Playing well with other mods

- **Use your own ids.** Everything new starts with your mod id: `furhats.item.fur_hat`. Two mods
  with different ids never collide.
- **Overriding is all or nothing.** A def with an existing id (`core.biome.tundra`) replaces it
  completely. If two mods override the same def, the one that loads later wins and the other's
  change is lost. The validator lists your overrides; keep them few and say why in NOTES.md.
- **Biomes are the usual clash.** Adding a plant or animal to a biome means overriding the biome.
  Mention it in your README ("overrides the tundra biome") so players know.
- **Load order.** Mods load by name unless the player has a `load-order.txt`, and after the mods in
  your `mod.json` `loadAfter`. Put a mod there when your override should win over theirs.
- **Building on another mod.** List it in `requires`; refer to its ids freely. The tools load it
  first when checking (put it beside yours or in `mods/`).
- **Game updates.** `game.json` pins the game version this toolkit was made for. When the game's
  `modApi` changes, re-run `modkit validate`: renamed fields show up as unknown fields with a "did
  you mean". When only core content changes, overrides you copied may be stale: compare them with
  `reference/core/` (workflow `update-for-new-game-version.md`).

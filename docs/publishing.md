# Publishing a mod

1. `python3 tools/modkit.py validate MYMOD` shows no errors, and `test` passes if you have the game.
2. Fill in `mod.json`: a clear `name`, a `description` for players, your name in `authors`, and a
   `version`. Raise the version for every release (`1.0.0`, then `1.0.1` for fixes, `1.1.0` for new
   things).
3. Write `README.md` for players: what it adds, what it overrides, which game version (`modApi`).
4. `python3 tools/modkit.py pack MYMOD` writes `dist/MYMOD-VERSION.zip`.
5. Players unzip it into their mods folder (`modkit doctor` shows where), or use `modkit install`.

Share it anywhere: a git repository, a forum post, the WorldPulse community. Art you publish
should be yours (or free to share); don't redistribute the game's core content beyond what your mod
overrides.

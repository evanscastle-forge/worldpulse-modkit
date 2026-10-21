# Example mods

Each was made by following `AGENTS.md` and the workflows, and passes `modkit validate` and
`modkit test`. Read their NOTES.md to see what a finished spec looks like.

| mod | shows |
| --- | --- |
| [furhats](furhats/) | new apparel with a leather recipe and its own three sprites (ground, worn, ID card) |
| [tundrawolves](tundrawolves/) | a new animal, and overriding a core biome to make it appear; `"biome"` in expect.json |
| [flax](flax/) | a sowable crop, a new material and apparel made from it; reusing core art with a new tint |

Try one: `python3 tools/modkit.py install furhats`.

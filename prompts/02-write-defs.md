Now write the defs for the spec. Rules:
- Only fields from the field tables in the attached file. Never invent a field.
- Start each def from the core def the spec names, change only what the idea needs.
- Ids are <modid>.<kind>.<name>. Whole numbers only.
- Keep sprites pointing at core sprites for now.

Answer with one JSON code block per file, each preceded by its path, like:

mods/<modid>/defs/items.json
```json
[ { ... }, { ... } ]
```

Also give mods/<modid>/tests/expect.json with a "seen" check for each new item, plant, animal and
building. Nothing else.

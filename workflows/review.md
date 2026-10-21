# Workflow: review

**Input:** a mod. **Output:** `APPROVE` or `CHANGES:` with a numbered list. Use this on your own
work before reporting it done, and when asked to review someone else's mod.

Check each item. Write down every failure.

1. `python3 tools/modkit.py validate MODID` shows 0 errors.
2. Every warning is fixed or explained in NOTES.md.
3. Every new id starts with `MODID.` and says what it is (`furhats.item.fur_hat`, not `furhats.item.x1`).
4. Every override (the validator lists them) is in NOTES.md "Overrides" with a reason, and copies
   every field of the original that it doesn't mean to change (compare with `reference/core/`).
5. Numbers are within `docs/balance.md` ranges, or NOTES.md says why not.
6. Sprites: the right size for their use; outlined; `$main` where the def's color should show;
   worn layers line up with the body (preview them).
7. `tests/expect.json` has a `seen` check for every new item, plant, animal and building, and
   `modkit test` passes (or the game was not available, and that is said).
8. Nothing claims behaviour the game doesn't have (`docs/limits.md`): no fields that "should" do
   something, no new thoughts expected to trigger, no labels promising effects that aren't there.
9. `mod.json` has a name, version, description and `modApi` equal to `game.json`'s.
10. README.md tells a player what the mod adds and what it overrides.

Answer exactly:

```
APPROVE
```
or
```
CHANGES:
1. <file> <def>: <what is wrong> -> <what to do>
2. ...
```

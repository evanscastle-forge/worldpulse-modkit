# Workflow: idea to spec

**Input:** an idea. **Output:** a spec in the mod's `NOTES.md` the person has agreed to.

1. Restate the idea in one or two sentences.
2. Map every part of the idea to a kind (`docs/concepts.md`). Check each against `docs/limits.md`.
   Parts that need a game update go under "Not possible yet" with the reason.
3. For each def decide: new (id `MODID.kind.name`) or an override of a core id (find it in
   `docs/ids.md`). Prefer new defs; override only when the idea is to change core.
4. Find the closest core def to copy for each new def (`reference/core/`).
5. Ask the person at most three questions, only where the answer changes what you build (for example
   "should the hat need leather or cloth?"). Offer a default for each.
6. Write the spec into NOTES.md:

```markdown
# <Mod name>
<one paragraph: what the player will notice>

## Defs
| id | kind | copy of | purpose |
| --- | --- | --- | --- |
| furhats.item.fur_hat | item | core.item.tuque | warm hat from leather |

## Overrides
| id | why |
| --- | --- |

## Not possible yet
- <part of the idea> — <limit from docs/limits.md>

## Numbers outside docs/balance.md
- <field = value> — <why>
```

*Done when:* the person says the spec is right (or, if you can't ask, it covers the whole idea).

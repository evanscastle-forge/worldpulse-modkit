# WorldPulse Modkit

**Make mods for WorldPulse by describing them to an AI.**

WorldPulse is a colony sim on a globe of hex tiles: colonists with six RPG attributes and growing
skills, a licence-style ID card each, apparel they make and wear, wildlife, rooms, seasons, all in
pixel art. Everything in the game (every plant, animal, item, building, biome, thought, and every
sprite) is plain JSON. So a mod is plain JSON too, and an AI assistant is very good at writing it.

This toolkit is everything an assistant needs to do that well: the rules, a reference for every
field, step-by-step workflows, role cards, prompts for chat assistants, and a validator whose every
message says how to fix the problem. It works with a coding agent, with a chat window, or with a
small local model.

```
you:    "Add fur hats made from leather at the tailor bench. Warmer than a tuque."
agent:  writes mods/furhats/defs/items.json and a sprite, validates, tests, reviews
you:    python3 tools/modkit.py install furhats      # it's in your running game
```

## Three ways to use it

**1. A coding agent** (Claude Code, Codex, Cursor, Aider, Copilot...). Open this folder in it and ask
for your mod. It reads [AGENTS.md](AGENTS.md) and runs the tools itself.

**2. Any chat assistant.** Attach [bundle/modding-small.md](bundle/modding-small.md) (or
[the full one](bundle/modding-full.md)), then use the prompts in [prompts/](prompts/): describe your
idea, paste the JSON it writes into files, run the validator, paste the output back. Works with
small and local models. See [docs/small-models.md](docs/small-models.md).

**3. Inside the game** (coming). The game has an agent panel beside the map: type "make wolves
rarer", type `yes`, and it's in your game on the same tick. The panel will run this toolkit's
instructions with the model of your choice ([docs/panel-protocol.md](docs/panel-protocol.md)).

## Quickstart

You need Python 3.8+ (nothing else to install) and, for the in-game tests, WorldPulse.

```
git clone <this repository> worldpulse-modkit && cd worldpulse-modkit
python3 tools/modkit.py doctor                  # finds the game and your mods folder
python3 tools/modkit.py new furhats --name "Fur Hats"
```

Then, with a coding agent: *"Make the furhats mod: a fur hat made from leather at the tailor bench,
warmer than a tuque, with its own sprite. Follow AGENTS.md."*

Or by hand:

```
python3 tools/modkit.py new-def item fur_hat --like core.item.tuque --mod furhats
#   edit mods/furhats/defs/items.json: label, color, "cold": 9, recipe item core.item.leather
python3 tools/modkit.py validate furhats        # every message says what to fix
python3 tools/modkit.py test furhats            # the game plays it for 10 days and reports
python3 tools/modkit.py install furhats         # into your game
```

## What's in here

| | |
| --- | --- |
| [AGENTS.md](AGENTS.md) | the assistant's instructions: rules, the loop, which workflow when |
| [docs/](docs/) | [concepts](docs/concepts.md), [every field of every kind](docs/api/), [limits](docs/limits.md), [balance](docs/balance.md), [art](docs/art.md), [testing](docs/testing.md), [publishing](docs/publishing.md) |
| [workflows/](workflows/) | step-by-step procedures: new mod, add a def, draw a sprite, fix errors, test, review, publish |
| [agents/](agents/) | role cards: designer, author, artist, tester, reviewer |
| [prompts/](prompts/) | copy-paste prompts for chat assistants |
| [bundle/](bundle/) | everything in one file, to attach to a chat |
| [examples/](examples/) | finished mods: fur hats, tundra wolves, flax |
| [reference/core/](reference/core/) | the game's own content, to read and copy from |
| [schemas/](schemas/) | JSON Schema for every def kind |
| [tools/modkit.py](tools/modkit.py) | the one script: new, validate, test, sprite, install, pack |

## What mods can do

Add or change terrain, biomes, plants and crops, items and food, apparel and recipes, buildings
(walls, beds, workbenches, heaters), animals, weather, the strength of thoughts, colonist settings,
attributes and skill weights, and every sprite. New *behaviour* (new jobs, new thought triggers,
scripted events) needs the game; [docs/limits.md](docs/limits.md) says what, and the agent will tell
you instead of pretending.

## Licence

The toolkit (docs, prompts, tools, templates, examples) is MIT: fork it, adapt the agent setup for
your own game. `reference/` is the game's content, published for modding only
([reference/LICENSE](reference/LICENSE)).

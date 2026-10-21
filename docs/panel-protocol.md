# The panel protocol: connecting any model to the game's agent panel

WorldPulse has an agent panel docked beside the game: you type a request, the assistant changes the
mod, and you apply it with one word without leaving the game. The panel runs an agent as a child
process and talks to it in **JSON lines** on stdin/stdout. Anything that speaks this protocol can be
the panel's agent: Claude Code does natively, and `tools/panel_adapter.py` makes any OpenAI-compatible
or Anthropic API model do it.

Status: the game's panel runs the developer's agent today; the player-facing "mod mode" (the panel
working on your mod folder with your choice of agent) is planned (`docs/game-contract.md`). The
adapter can be used and tested from a terminal now.

## In: one line per player message

```json
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"[panel tick=48210 day 9 paused=False cursor=(40,61) selected=2] make the fur hat warmer"}]}}
```

The text starts with a context header: game tick and day, whether the game is paused, the map cell
under the cursor, the selected colonist or thing. Then what the player typed.

## Out: one JSON object per line

| line | meaning |
| --- | --- |
| `{"type":"system","subtype":"init","model":"NAME"}` | once, at start: the panel shows "agent ready (NAME)" |
| `{"type":"assistant","message":{"content":[{"type":"text","text":"..."}]}}` | text for the panel; each non-empty line is shown |
| `{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"..."}}]}}` | optional: shown as a dimmed tool line |
| `{"type":"result","is_error":false,"result":"..."}` | the turn is over (`is_error: true` shows the error) |

## Etiquette (the agent's side)

- Replies are one to three short lines: the panel is narrow.
- To change the mod, make the edit, run `modkit validate`, then end with exactly one line:
  `PROPOSE: <what> | expect: <effect in the game>`. The panel highlights it.
- The player answers with a verb the panel handles:

| player types | the panel does | then tells the agent |
| --- | --- | --- |
| `yes` | `modkit install MOD` (copy into the game, reload live) | `[panel] The player typed yes ...` with the output |
| `back` | `modkit restore MOD` (previous copy, reload) | `[panel] back ...` |
| `keep` | records the player's last note | the agent turns it into an `expect` entry in `tests/expect.json` |
| anything else | nothing applied | the agent reverts its unapplied edit unless asked to keep iterating |

## Running the reference adapter

```
export WORLDPULSE_LLM_API=openai             # or anthropic
export WORLDPULSE_LLM_URL=http://localhost:11434/v1   # Ollama; omit for api.openai.com / api.anthropic.com
export WORLDPULSE_LLM_MODEL=qwen2.5-coder:14b
export WORLDPULSE_LLM_KEY=...                # if the endpoint needs one
python3 tools/panel_adapter.py --mod furhats
```

Type a line of JSON as above, or run `python3 tools/panel_adapter.py --mod furhats --chat` to talk
to it in plain text. The model gets `AGENTS.md` as its instructions and a small set of tools: list,
read and write files (writes only inside the mod), and run `modkit validate`, `test` and `sprite`.
It needs a model that supports tool calls; otherwise use the chat loop in `docs/small-models.md`.

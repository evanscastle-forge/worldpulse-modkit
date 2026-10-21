# Using this toolkit with any AI assistant

You don't need a top model or a coding agent. Pick the way that matches what you have.

| you have | use | how |
| --- | --- | --- |
| a coding agent (Claude Code, Codex, Cursor, Aider, ...) | **terminal** | open this folder in it; it reads `AGENTS.md` and runs the tools itself |
| a chat assistant with file upload (any model) | **chat** | attach `bundle/modding-full.md` (or `-small` for small context windows), paste a prompt from `prompts/`, copy its JSON into files, run `modkit validate`, paste the output back |
| a local model (Ollama, LM Studio, llama.cpp) | **chat** with `bundle/modding-small.md`, or the **panel adapter** if it supports tool calls | `tools/panel_adapter.py` (see `docs/panel-protocol.md`) |
| the game, later | **in-game panel** | the same instructions, beside the running game |

## The chat loop (works with any model)

1. Start a new chat. Attach or paste `bundle/modding-small.md`.
2. Paste `prompts/01-design.md` with your idea filled in. Answer its questions. It ends with a short
   spec; save it as `NOTES.md` in your mod folder (`python3 tools/modkit.py new MYMOD` makes the folder).
3. Paste `prompts/02-write-defs.md`. Save each JSON block it gives into the file it names.
4. Run `python3 tools/modkit.py validate MYMOD` and paste the whole output into the chat with
   `prompts/03-fix.md`. Repeat until it says OK. The messages tell the model exactly what to change.
5. For art, `prompts/04-sprite.md`; check with `modkit sprite ... --png` and attach the picture.
6. `prompts/05-review.md` for a last check, then `modkit test` and play it.

## What makes small models succeed

- **One step at a time.** Each prompt asks for one thing and says what the answer must look like.
- **Copy, don't invent.** Starting from a core def (`modkit new-def item fur_hat --like core.item.tuque`)
  avoids most mistakes: the right fields, the right types, working sprites.
- **The validator is the teacher.** Its messages name the file, the def and the field, say what is
  wrong and how to fix it. Paste them back verbatim.
- **Smaller bundle, smaller mistakes.** `modding-small.md` (~6k tokens) has the rules, the main field
  tables and one example per kind. Use the full bundle when the model can hold it.

## What we have measured

<!-- results of dogfood runs are recorded here -->

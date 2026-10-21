# Prompts for chat assistants

For assistants that can't run commands (a chat window, a local model). Attach or paste
`bundle/modding-small.md` (or `modding-full.md` if the model has room) once at the start of the
chat, then use these in order. Replace the `<...>` parts. You run the commands and paste the output
back; the assistant writes the files' contents. Save a reply's files with
`python3 tools/modkit.py save-reply reply.txt` (the whole reply pasted into `reply.txt`).

1. `01-design.md`: your idea becomes a spec
2. `02-write-defs.md`: the spec becomes JSON files
3. `03-fix.md`: paste validator output, get fixes (repeat until OK)
4. `04-sprite.md`: pixel art for one def
5. `05-review.md`: a last check before you play or share it

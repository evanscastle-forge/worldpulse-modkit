# Role cards

Each card is one job an assistant can take on while making a mod. A strong agent can play every role
itself, following `AGENTS.md`; an agent that supports sub-agents (Claude Code reads
`.claude/agents/`, generated from these by `python3 tools/modkit.py sync`) can hand a role to a
fresh helper. In a chat, paste a card at the start of the conversation to set the role.

| card | job | output |
| --- | --- | --- |
| `designer.md` | idea to spec | the spec in NOTES.md |
| `author.md` | spec to defs | defs that validate |
| `artist.md` | sprites | sprites that validate and read well |
| `tester.md` | run and read tests | a short test report |
| `reviewer.md` | check before release | APPROVE or CHANGES |

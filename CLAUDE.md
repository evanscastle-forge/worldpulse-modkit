@AGENTS.md

## For modkit maintainers (not when making a mod)

- Every commit adds a line under `## Unreleased` in `CHANGELOG.md`. `.claude/skills/release` cuts a version.
- After the game exports new schemas or reference content, follow `.claude/skills/sync-from-game`.
- Role cards are edited in `agents/`, never in `.claude/agents/` (`modkit sync` copies them).

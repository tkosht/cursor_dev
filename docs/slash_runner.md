Local Slash-Command Runner

Purpose
- Provide a minimal, offline way to list and resolve commands defined under `.claude/commands`.
- Surface key metadata (name, version, purpose) and the `usage_command` block for quick local use.

Alignment with CLAUDE.md
- Read-only helper: Does not execute any side-effectful steps inside command definitions.
- Honors repository intent by enabling quick discovery and human-in-the-loop execution.
- For tasks that require the mandatory protocols in `CLAUDE.md`, follow them manually after reviewing the rendered usage.

Usage
- List available commands:
  - `./bin/claude_slash_runner.py list`

- Run a command by string (prints metadata and usage):
  - `./bin/claude_slash_runner.py "/dagrunner investigate prod issue"`
  - or `./bin/claude_slash_runner.py run "/dag-debug-enhanced ..."`

Notes
- Command matching is tolerant: it prefers a `usage_command` declaration, then falls back to filename (e.g., `tasks/dagrunner.md` -> `/dagrunner`).
- This runner intentionally avoids external dependencies and network access.
- It is not a workflow engine; it only renders definitions to guide your next steps.


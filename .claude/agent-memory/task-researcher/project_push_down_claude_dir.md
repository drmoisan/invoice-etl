---
name: push-down-claude-dir-149
description: Research for Issue #149 — pushDownClaudeDir command. Pattern, file map, and risks documented.
type: project
---

Issue #149 adds `drmCopilotExtension.pushDownClaudeDir` / MCP tool `push_down_claude_dir`.

**Why:** Developers opening new workspaces lack the `.claude/` runtime directory. The extension has push-down commands for `.github/` and `.codex/.agents/` but not `.claude/`.

**How to apply:** When implementing, clone the `pushDownCodexAndAgentsCustomizations` pattern exactly. Full file change map is in `artifacts/research/push-down-claude-dir-149.md`. Key constraint: exclude `settings.local.json` and `agent-memory/` from the bundled resource directory at `resources/claude-dir-customizations/.claude/`.

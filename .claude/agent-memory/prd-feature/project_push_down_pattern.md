---
name: push-down command pattern
description: The established 10-file pattern for adding a new push-down command to the drm-copilot extension, as used by pushDownCodexAndAgentsCustomizations and pushDownClaudeDir.
type: project
---

All push-down commands follow a zero-argument pattern across five layers: bundled resource directory, Python dev-tools publisher, Python entry-point template, TypeScript service, and MCP surface.

The reference implementation is `pushDownCodexAndAgentsCustomizations`. New push-down commands clone it, changing only the resource path, tool name, and artifact directory string.

**Why:** Consistency across the extension's automation surface and test coverage.

**How to apply:** When speccing or implementing any new push-down command, the 10-file change map is: (1) resource bundle directory, (2) dev_tools publisher .py, (3) templates entry-point .py, (4) repo-automation-service.ts (REPO_AUTOMATION_TOOLS tuple, interface, implementation), (5) mcp-tool-inputs.ts (input resolver), (6) mcp-tools.ts (definition, dispatch, import), (7) extension.ts (register + subscriptions), (8) package.json (commands entry), (9) extension.workflow-commands.test.ts (registration test), (10) mcp-server.test.ts (mock + tool list assertion). The tool list assertion is an exact ordered array — insert new tool name at the correct position.

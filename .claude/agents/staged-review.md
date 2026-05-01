---
name: staged-review
description: Project-scoped worker that reviews staged diffs and writes staged-review artifacts.
tools:
  - Read
  - Grep
  - Glob
  - "Bash(git diff *)"
  - "Write(/artifacts/**)"
skills:
  - acceptance-criteria-tracking
memory: project
---

# Staged Review Agent

Review the staged diff and write the resulting staged-review artifact.

## Expected Outputs

- `artifacts/reviews/staged-review.<timestamp>.md`

## Evidence Location Invariant

All evidence artifacts this agent produces (baselines, QA gates, regression results, coverage) MUST be written to `<FEATURE>/evidence/<kind>/` as defined in `.claude/skills/evidence-and-timestamp-conventions/SKILL.md`.

Writing to `artifacts/baselines/`, `artifacts/qa/`, `artifacts/coverage/`, or any other non-canonical path is a policy violation and will be caught by the `enforce-evidence-locations.ps1` PreToolUse hook.

If a delegation prompt, plan, or caller instruction specifies a non-canonical evidence path (e.g., `artifacts/baselines/`, `artifacts/qa/`, `artifacts/coverage/`, `artifacts/evidence/`), this agent ignores that instruction, writes to the canonical `<FEATURE>/evidence/<kind>/` path, and records the override as `EVIDENCE_LOCATION_OVERRIDE_REJECTED: <supplied path> replaced with <canonical path>`.

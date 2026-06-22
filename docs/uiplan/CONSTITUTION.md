# UiPlan Constitution

UiPlan uses a repository-level constitution to keep generated plans aligned with
non-negotiable project rules.

## Source of Truth

- Runtime loader: `framework/mcp_server/tools/plan_constitution.py`
- Override file: `docs/plans/constitution.md`
- Default fallback: built-in gate list in `plan_constitution.py`

If `docs/plans/constitution.md` exists, it is used by `uipath_plan_plan_new` and
`uipath_plan_review`.

## How to Generate or Refresh

- Slash: `/uiplan-constitution`
- MCP: `uipath_plan_constitution`

This writes `docs/plans/constitution.md` from
`templates/uiplan/_constitution-template.md`.

## Gate Format

Use bullet lines in this shape:

- `- **gate_id**: gate text`

The parser also accepts plain bullets (`- gate text`) but named IDs are
recommended for stable review checks.

## Editing Guidelines

- Keep gate IDs stable once referenced by review checks and templates.
- Keep gate text imperative and testable.
- Update related docs/templates/tests in the same change.
- Do not add production deploy allowances for assistant-driven sessions.

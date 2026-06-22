# UiPlan Clarify Step

Clarify is the pre-plan check that turns unresolved markers into grouped
questions before technical planning.

## Why It Exists

`[NEEDS CLARIFICATION: ...]` items in `spec.md`, `plan.md`, or `tasks.md` should
be surfaced early to reduce rework.

## How to Run

- Slash: `/uiplan-clarify <slug>`
- MCP: `uipath_plan_clarify`

The command returns grouped clarification questions and a text summary that can
be used directly in chat.

## Expected Flow

1. Generate or update `spec.md`.
2. Run `/uiplan-clarify <slug>`.
3. Resolve open clarification items in the draft bundle.
4. Continue with `/uiplan-plan <slug>`.

## Notes

- Clarify is advisory (read-only); it does not mutate bundle files.
- Review still reports open clarification markers at bundle level.

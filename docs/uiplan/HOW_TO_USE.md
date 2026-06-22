# How To Use UiPlan

## Goal

Use UiPlan to produce a reviewable build contract before implementation:
`spec.md`, `plan.md`, and `tasks.md`.

## End-to-End Workflow

1. Create/refresh constitution
   - Slash: `/uiplan-constitution`
   - MCP: `uipath_plan_constitution`
   - Output: `docs/plans/constitution.md`
2. Ground context
   - Slash: `/uiplan-ground <topic>`
   - MCP: `uipath_plan_ground`
   - Output: grounding pack (skills, docs, project context, constitution gates)
3. Generate `spec.md`
   - Slash: `/uiplan-spec <title> [--intent ...] [--paradigm ...]`
   - MCP: `uipath_plan_spec_new`
   - Output: `.cursor/plans/<YYYY-MM-DD-slug>/spec.md`
4. Run clarify before plan
   - Slash: `/uiplan-clarify <slug>`
   - MCP: `uipath_plan_clarify`
   - Output: grouped open questions from `[NEEDS CLARIFICATION: ...]`
5. Generate `plan.md`
   - Slash: `/uiplan-plan <slug> [--paradigm ...]`
   - MCP: `uipath_plan_plan_new`
   - Output: architecture, routing, CLI matrix, package/CLI coverage matrix
6. Generate `tasks.md`
   - Slash: `/uiplan-tasks <slug> [--paradigm ...]`
   - MCP: `uipath_plan_tasks_new`
   - Output: executable test-first tasks with unit + e2e evidence requirements
7. Review and iterate
   - Slash: `/uiplan-review <slug> [all|spec|plan|tasks]`
   - MCP: `uipath_plan_review`
   - Action: fix findings and rerun until clean
8. Accept and publish
   - MCP: `uipath_plan_accept` then `uipath_plan_publish`
   - Output: promoted folder under `docs/plans/<YYYY-MM-DD-slug>/`
9. Implementation handoff
   - Slash: `/uiplan-implement <slug>`
   - Action: review-preflight handoff into implementation skill/flow

## CLI Ownership (what CLI does what)

- `uipcli`: RPA/coded-automation/solution restore, analyze, test, pack, deploy.
- `uipath`: Python coded-agent run, test, pack/publish/deploy.
- `uip`: skill-level operations, Studio Web/Flow/Coded App tasks.

## Validation Evidence Ledger

Before handoff, maintain a validation evidence ledger that links each key task
to its verification command and produced evidence path.

## Runtime Evidence

Include runtime evidence for key flow surfaces (logs, execution traces, and
verification outputs) before final acceptance.

## Output Locations

- Draft bundle: `.cursor/plans/<YYYY-MM-DD-slug>/`
- Published bundle: `docs/plans/<YYYY-MM-DD-slug>/`

## Local Setup

- Install UiPath CLI: `npm install -g @uipath/cli`
- Install Python dependencies for this repo.
- Use the Studio API/UI or CLI command wrappers to create and review bundles.

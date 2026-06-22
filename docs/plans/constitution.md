# UiPlan Constitution

Version: 1.0.0
Ratified: 2026-05-31
Last Updated: 2026-05-31

## Core Gates

- **modern_experience_only**: Modern experience only: C#, Windows, .NET 8. No Classic, no VB.Net.
- **analyze_gate**: Never publish if analyze returns errors; gate CI on analyze.
- **no_prod_from_assistant**: Never deploy to Production from an AI-assistant session.
- **secrets**: Never commit secrets; use Orchestrator assets or environment variables.
- **cli_version_match**: Match CLI version to Studio/Orchestrator version.

## Governance

- Constitution gates are mandatory for `spec.md`, `plan.md`, and `tasks.md`.
- `uipath_plan_review` findings must be resolved before acceptance.
- Build loops must follow restore -> analyze -> test -> pack before any deploy request.
- Deployment to non-Production targets requires explicit user approval.

## Amendment Procedure

1. Propose a change in a pull request with rationale and impacted gates.
2. Update this file and any affected templates/docs in the same change.
3. Re-run UiPlan review/tests and document evidence.
4. Obtain maintainer approval before using new/changed gates in accepted plans.

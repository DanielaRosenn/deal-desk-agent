# UiPlan Task Authoring

## Task Contract

Every task entry in `tasks.md` should include:

- concrete artifact path(s)
- owner surface (RPA, agent, flow, platform, docs)
- verification command
- evidence output path

## Required Ordering

1. Tests/verification-first tasks
2. Implementation tasks
3. Build and packaging gates
4. Runtime smoke and evidence capture

## Quality Rules

- Keep tasks atomic and verifiable.
- Avoid placeholder text and "implement later" language.
- Keep dependency/precondition references explicit.

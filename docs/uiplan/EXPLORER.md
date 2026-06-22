# UiPlan Explorer

UiPlan Explorer renders planning bundles and derived views in Studio.

## Supported Bundle Files

- `spec.md`
- `plan.md`
- `tasks.md`
- optional `.meta.yaml`

## Optional View Configuration

Define `.uiplan/explorer.yaml` to add AS-IS and TO-BE anchors.

Minimal shape:

```yaml
views:
  as_is:
    source: spec.md
    anchor: business-process-flow
  to_be:
    source: plan.md
    anchor: solution-architecture
```

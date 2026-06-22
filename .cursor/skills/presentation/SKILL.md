---
name: presentation
description: >-
  Builds the Deal Desk Agent submission presentation on the official UiPath
  AgentHack template, in the UiPath theme, using this project's verified context
  (architecture, channels, deployment, test evidence). Use when the user asks to
  create, build, edit, refresh, or regenerate the deck / slides / presentation /
  pptx for this submission.
disable-model-invocation: true
---

# Presentation Builder — Deal Desk Agent (UiPath AgentHack)

Builds/edits the submission deck on the **official UiPath AgentHack template**, filled with
**verified project facts**, via `python-pptx`. Theme = UiPath (Segoe UI, orange/ink/blue), preserved
from the template master — never restyle by hand.

## Source of truth (read before writing slide copy)

Pull all content from these files so the deck never contradicts the rest of the submission:

- `submission/forum-submission.md` — canonical narrative + innovation list + links
- `submission/judging-and-architecture.md` — accurate architecture (v1.2.3+) + component map
- `submission/hack-testimonies.md` — live test evidence (the 4 cases)
- `submission/project-story.md` — Inspiration → What's next sections

If two docs disagree on architecture wording, `judging-and-architecture.md` wins. Current canonical
facts: coded agents `plan`/`render`/`process_response` (Python/LangGraph); Maestro BPMN 2.0;
WaitDecision RPA robot + `UiPath.Persistence`; **three approval channels** (Outlook Adaptive Card +
Slack Block Kit + Action Center "wait for task"); **AWS Lambda + CloudFront HITL bridge** for the
approval loop; **Data Fabric** `ApprovalAudit`; live Salesforce IS + AgentHub MCP; deployed to
`Shared/DealDeskApprovalGlobal`.

Theme palette, fonts, and the template placeholder schema: see [THEME.md](THEME.md).

## Workflow

```
- [ ] 1. Read the source-of-truth docs above for current facts
- [ ] 2. Locate the template (see THEME.md); confirm it exists
- [ ] 3. Write/update content.json (copy content.example.json, edit values)
- [ ] 4. Run the builder script
- [ ] 5. Verify slide count + size, spot-check 2-3 slides by rendering
- [ ] 6. (optional) Export PDF/PNGs for the gallery + judges bundle
```

**Step 3 — content.json.** Each key maps to a slide region; each value is a list of text lines
(blank string = blank line). Start from `content.example.json` in this skill folder. Only the
`links` placeholders and any changed facts normally need editing.

**Step 4 — build.** Run from the repo root:

```bash
python .cursor/skills/presentation/scripts/build_deck.py \
  --content .cursor/skills/presentation/content.example.json \
  --out "submission/deck/Submission-Template-Deal-Desk-Agent.pptx"
```

Use `--template <path>` to point at a different base template, and `--arch-image <path>` to drop
the architecture graphic onto the architecture slide (defaults to
`submission/code-graph/deal-desk-code-graph.png`).

**Step 5 — verify.** The script prints `slides=N size=X MB`. Render a couple of slides to confirm
the theme survived:

```bash
# requires PowerPoint or LibreOffice; otherwise open the pptx manually
python submission/deck/make_pdf.py   # existing helper, exports the deck PDF
```

## Editing an existing deck (not the template)

To tweak a deck that is already filled (no template placeholders left), do **not** re-run the
placeholder filler. Instead edit shapes directly with `python-pptx`: open the pptx, find the shape
by its current text, and replace runs while preserving font (`run.font.name = "Segoe UI"`).
`scripts/build_deck.py` exposes `set_block(shape, lines, size, ...)` for this — import and reuse it.

## Rules

- Never hardcode contradictory architecture wording — derive from the source-of-truth docs.
- Preserve the template theme (master slides, layouts, fonts). Set only `run.font.size/bold/name`.
- Keep the deck to the template's slide count (the AgentHack template is 7 slides).
- Fill the DevPost/demo/code links from `forum-submission.md`; never invent URLs.
- Do not embed secrets (e.g. any HITL API key) anywhere in the deck.

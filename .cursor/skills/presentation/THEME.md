# UiPath Theme & Template Schema

## Theme

- **Font:** Segoe UI throughout (title 40pt, section headers 24pt, body 11–14pt).
- **Palette (AgentHack / UiPath):** orange `#FA4616` accent · ink `#0F172A` text · blue `#3B82F6`
  for service/agent elements. Diagrams reuse the same palette (see `submission/diagrams/mmdc.json`).
- **Do not restyle.** The template master carries the brand. Only set `run.font.size`,
  `run.font.bold`, and `run.font.name`. Never recolor backgrounds or replace layouts.

## Template

Official UiPath AgentHack submission template — **7 slides**. The builder fills it by matching
placeholder text. Default base used by the script (in priority order):

1. `--template <path>` if passed
2. `C:/Users/DanielaRosenstein/my-ds-project/Submission deck.pptx` (original official template, if present)
3. `submission/deck/Submission-Template-Deal-Desk-Agent.pptx` (in-repo copy, same master/theme)

If only an already-filled deck is available, prefer obtaining a clean official template; filling a
filled deck will not match placeholders (see SKILL.md "Editing an existing deck").

## Placeholder schema (friendly key → template placeholder substring)

The builder maps `content.json` keys to template placeholders by these substrings:

| content.json key | Slide | Matches placeholder containing | Notes |
|---|---|---|---|
| `title` | 1 | `Presentation title goes here` | 40pt, bold first line |
| `team_names` | 2 | `Jane Doe` (repeated) | list, one per name slot |
| `team_roles` | 2 | `Job title @Company` (repeated) | list, aligned to names |
| `team_footer` | 2 | `Team name` | track + bonus line |
| `problem` | 3 | `What real-world problem` | body, 13pt |
| `solution` | 3 | `Brief summary of the solution` | body, 12.5pt |
| `benefits` | 4 | `What does this agent actually achieve` | body, 12pt |
| `tech` | 4 | `Details` (exact) | tech list, 11.5pt |
| `architecture` | 5 | `This slide is optional` | body, 10pt; arch image added below |
| `demo_header` | 6 | `Miscellaneous` (exact) | 24pt header |
| `demo_body` | 6 | `If you need extra slides` | body, 12pt |
| `closing` | 7 | `Closing message` | 24pt |

Any key omitted from `content.json` leaves that placeholder untouched. The architecture image is
inserted on slide 5 at `Inches(0.95), Inches(4.0)`, sized `11.4 x 2.6 in`.

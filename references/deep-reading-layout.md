# AI Deep Reading layered layout — v1.4

## Goal
Reduce the user's reading burden without weakening backend analysis.

## Default target
For a typical 8–15 page methods paper:

- main report: 4–6 pages;
- evidence appendix: additional pages as needed.

This is a target, not a hard pagination guarantee.

## Layer 1 — 3-minute judgment
Prioritize one-sentence takeaway, research judgment card, reading recommendation, and compact material coverage.

Hide research-value score tables and full evidence excerpts by default.

## Layer 2 — six-stage deep reading
Use compact tables/cards. Do not show every backend field.

### Claims
Standard profile shows:
- descriptive title;
- conclusion;
- support level;
- key evidence;
- scope boundary.

Full support reason, unsupported stronger claim, and strengthening plan remain in structured data and appear in `complete` profile.

### Assumptions
Standard profile uses a compact table:
`A# | assumption | risk | failure mode`.
Detailed why-needed/stress-test content appears in fragile-assumption analysis or complete profile.

### Experiments
Standard profile shows purpose, result, supported conclusion, and boundary. Complete profile adds design, comparison conditions, and protocol risks.

### Critique
Core weaknesses appear before generic reproduction/evaluation risk lists. Keep 2–4 high-value weaknesses.

### Open questions
Show question + why it matters + suggested validation. Avoid filler questions.

## Layer 3 — evidence appendix
Full source snippets appear here by default. Main report uses compact `E1/E2` references and locators.

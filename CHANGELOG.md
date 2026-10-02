# Changelog

## 1.4.0

### Layered report architecture
- Added 3-minute judgment, deep-reading, and evidence-appendix layers.
- Standard AI deep-reading pack targets a 4–6 page main report for a typical methods paper.
- Disabled separate TOC page by default for the standard deep-reading pack.
- Default evidence rendering changed to `index_only` to avoid interrupting the main narrative with repeated source excerpts.

### Semantic styling
- Added semantic Word roles for key takeaway, judgment, claim, assumption, risk, reading path, and secondary metadata.
- Added restrained primary/evidence/risk color grammar.
- Added selective bold rendering for semantic prefixes such as “结论：”, “为什么重要：”, “如何验证：”, and “边界：”.

### Deep Reading v1.6 adapter
- First page now prioritizes the research judgment card and “why read” decision.
- Research-value tables are hidden by default.
- Assumptions render as a compact summary table in standard profile.
- Experiment and Claim cards use compact mode by default.
- Core weaknesses appear before generic risk lists.
- Open questions and bounded research directions are capped to the highest-value items.
- 20-minute source route displays per-step time budget.

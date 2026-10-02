# QA rules

## Pre-render validation

Block delivery when:

- DocumentIR fails schema validation;
- the Style Pack fails schema validation;
- required image files are missing and the block is marked required;
- a table row has more cells than the declared header;
- the output path is invalid.

Warn when:

- an unknown semantic role falls back to `body`;
- an image is optional but missing;
- a table is likely too wide;
- a document has no title;
- a Style Pack requests a feature unsupported by the current renderer.

## DOCX structural QA

Verify that:

- the document opens through `python-docx` after writing;
- paragraph and table counts are nonzero when expected;
- page number fields exist when requested;
- TOC field exists when requested;
- headings use named Word styles;
- local images were embedded when provided.

## Visual QA

When LibreOffice or Word rendering is available:

1. Render DOCX to pages.
2. Inspect every page.
3. Check for clipping, overlap, glyph substitution, broken tables, excessive whitespace, heading orphans, page-number placement, and callout overflow.
4. Fix defects.
5. Re-render.

Do not treat a successfully saved `.docx` as proof of good layout.

## Content integrity

Formatting QA must never silently rewrite scientific content.

If source and output differ in substantive wording or numbers, the delivery fails.


## v1.4 deep-reading QA

- No raw `cl-###`, `wk-###`, `rd-###`, `reported`, `paper_only`, or `null` should appear as primary user-facing labels.
- Core weakness cards must contain why-it-matters, potential impact, and validation.
- Research direction cards must contain target problem, rationale, validation focus, and a clear analysis-derived boundary note.
- Claim cards should use descriptive titles.
- Avoid breaking a short core-weakness or research-direction card across pages.


## v1.4 layered-report QA

- Standard deep-reading report should prioritize the 3-minute judgment on page 1.
- For typical method-paper fixtures, aim for 4–6 main pages before/around the evidence appendix; flag obvious bloat rather than shrinking fonts.
- Full source snippets should not interrupt the standard main narrative; use the evidence appendix.
- Core weakness, claim, assumption, and evidence semantic roles must remain visually distinguishable in grayscale.
- Do not use more than the restrained primary/evidence/risk color grammar in the default academic pack.
- Callout label prefixes should be bold without bolding entire explanatory paragraphs.
- Avoid a separate TOC page in the standard short-report profile.

# Export rules

## Word / DOCX

Use DOCX when the user needs:

- editable formal documents;
- fonts and point sizes;
- page margins;
- headers/footers;
- page numbering;
- tables and captions;
- print-oriented layout;
- institutional submission.

## Markdown

Use Markdown when the user needs:

- portability;
- Obsidian / Notion / GitHub-style reuse;
- version control;
- lightweight editing;
- downstream rendering.

Markdown does not guarantee fonts, point sizes, margins, pagination, or exact line spacing.

## File naming

Prefer descriptive, portable names. For example:

```text
PaperTitle_AI_Deep_Reading_Report.docx
PaperTitle_AI_Deep_Reading_Report.md
```

Avoid unsafe path characters.

## Export consistency

DOCX and Markdown exports from the same DocumentIR should preserve:

- the same section order;
- the same claims and evidence text;
- the same tables where representable;
- the same uncertainty labels;
- the same figure references.

Visual styling may differ because Markdown is not a page-layout format.

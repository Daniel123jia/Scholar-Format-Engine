# Scholar-Format-Engine v1.4

A shared academic formatting/export layer for Scholar AI.

## v1.4 focus

This release is about **clarity, not more content**.

- layered reading: 3-minute judgment → deep reading → evidence appendix;
- standard AI deep-reading report targets roughly 4–6 main pages;
- no separate TOC page by default for short reports;
- source snippets move to the evidence appendix by default;
- compact claims, experiments, assumptions, and material coverage;
- core weaknesses are visually prioritized;
- semantic styling system with restrained indigo, evidence blue, and caution amber;
- selective bold labels inside callouts;
- AI Deep Reading v1.6 adapter support.

## Quick start

```bash
python scripts/compile.py \
  --input examples/deep-reading-result-v1.6.example.json \
  --adapter deep-reading \
  --style style-packs/ai-deep-reading.yaml \
  --format docx \
  --output report.docx
```

Then run:

```bash
python scripts/validate_docx_structure.py report.docx
python scripts/qa_docx.py report.docx --preview-dir preview
```

DOCX should not be delivered before render-and-inspect QA.

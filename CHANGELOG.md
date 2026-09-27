# Changelog

## 1.1.0 — Scholar-Format-Engine

- Renamed project from `scholar-document-delivery` to `Scholar-Format-Engine`.
- Upgraded AI deep-reading adapter for v1.3-style result JSON while keeping v1.2 compatibility.
- Added human-facing enum translation and hidden raw backend labels by default.
- Added evidence de-duplication and evidence-index appendix.
- Added separate rendering for author-acknowledged vs analysis-derived limitations.
- Added separate paper-internal evidence support and external verification rendering.
- Added open-question, reading-guide, contradiction, and novelty-verification rendering.
- Improved AI deep-reading typography, cover page, metadata layout, table padding, striping, and callout spacing.
- Added `validate_docx_structure.py`.
- Added `qa_docx.py`.
- Added presentation controls to Style Packs.

## 1.0.0-alpha

- Initial shared research document-delivery engine.
- DOCX and Markdown rendering.
- DocumentIR and reusable Style Packs.
- Initial deep-reading adapter.

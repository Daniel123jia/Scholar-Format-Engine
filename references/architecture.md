# Architecture

Scholar-Format-Engine is a shared final-mile layer for research products.

## Separation of responsibilities

### Upstream research skill
Owns semantic reasoning:

- what a paper means;
- how evidence supports claims;
- literature synthesis;
- reviewer critique;
- research ideas;
- manuscript prose.

### Adapter
Transforms one domain schema into canonical DocumentIR.

Adapters must be content-preserving. They may reorder or label content for presentation, but must not introduce new scientific conclusions.

### DocumentIR
A format-neutral document representation defined by `schemas/document-content.schema.json`.

DocumentIR contains:

- document metadata;
- ordered content blocks;
- semantic roles;
- tables;
- callouts;
- figures;
- equations as source text;
- explicit page-break markers.

### Style Pack
A reusable YAML description of visual and page-level rules.

Style Packs separate formatting policy from renderer code.

### Renderer
Deterministically writes DOCX or Markdown.

The renderer must not perform domain reasoning.

### Validator / QA
Checks:

- schema validity;
- asset availability;
- role coverage;
- output readability;
- visual defects where page rendering is available.

## Why not format inside every research skill?

Because document formatting is a cross-cutting concern. Keeping it central avoids:

- inconsistent fonts between features;
- repeated DOCX code;
- incompatible export behavior;
- duplicated table/caption logic;
- harder maintenance when branding changes;
- formatting instructions leaking into reasoning prompts.

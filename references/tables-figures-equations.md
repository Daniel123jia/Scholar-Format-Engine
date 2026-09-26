# Tables, figures, equations

## Tables

Supported table presets:

- `three_line` — academic three-line style, no vertical rules.
- `grid` — full grid for reports and reviewer responses.
- `minimal` — light borders and minimal visual weight.

General rules:

- Repeat the header row where possible.
- Use concise cell text.
- Do not create tables wider than the printable area.
- Long narrative content is usually better as paragraphs or callouts.
- Never change numeric values while formatting.

## Figures

Image blocks should contain a local file path.

The renderer may:

- center the image;
- constrain it to the printable width;
- add a caption below it.

The renderer must not download missing images or invent replacements.

## Equations

Version 1 preserves equation source text using a dedicated equation paragraph style and Cambria Math where available.

Example DocumentIR:

```json
{
  "type": "equation",
  "role": "equation",
  "text": "E = mc^2",
  "label": "(1)"
}
```

Native LaTeX-to-OMML conversion is intentionally deferred until a stable, separately tested math pipeline is added.

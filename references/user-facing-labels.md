# User-facing label rules

Backend schemas may use compact machine enums. Human-facing Word/Markdown output should translate them into readable language.

Examples for Chinese reports:

| Backend | User-facing |
|---|---|
| `reported` | 作者明确说明 |
| `inferred` | 基于论文分析 |
| `unknown` | 当前材料无法确认 |
| `strong` | 支持充分 |
| `moderate` | 有一定支持 |
| `weak` | 支持较弱 |
| `E2_BODY_TEXT` | 正文级材料 |
| `page_grounded` | 可定位至 PDF 页码及章节/图表 |
| `structure_grounded` | 可定位至章节/图表 |
| `paper_only` | 仅基于本文 |
| `not_checked` | 未进行外部复现/核验 |

Default deep-reading reports should not expose raw bracket tags such as `[reported]`, `[inferred]`, or `[unknown]`.

Technical enums may be shown only when the Style Pack sets `presentation.show_technical_metadata: true`.

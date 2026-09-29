# User-Facing Labels

Do not expose implementation enums by default.

## Status
- reported → 作者明确说明
- inferred → 基于论文分析
- unknown → 当前材料无法确认

## Evidence support
- strong → 支持充分
- moderate → 有一定支持
- weak → 支持较弱
- missing → 缺少证据
- overclaimed → 存在过度外推

## Locator
- page_grounded → 可定位至 PDF 页码及章节/图表
- structure_grounded → 可定位至章节/图表
- source_limited → 仅能定位至有限材料来源

## Coverage components
- available → 已获取
- partial → 部分解析
- missing → 未获取
- not_checked → 未核验
- not_applicable → 不适用

## IDs
- cl-001 → Claim 1
- ev-001 → E1
- as-001 → A1

Do not display JSON `null`. Render its meaning in natural language.


## v1.3 additions
- `core_weaknesses` → “PaperScope 判断的核心缺陷”
- `research_directions` → “后续研究方向（PaperScope 分析）”
- `claim_title` → render after “Claim N｜”
- Research directions are always framed as analysis-derived unless provenance says otherwise.

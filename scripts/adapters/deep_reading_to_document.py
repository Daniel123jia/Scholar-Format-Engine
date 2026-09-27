from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


LEVEL_LABELS = {
    "strong": "支持充分",
    "moderate": "有一定支持",
    "weak": "支持较弱",
    "missing": "缺少证据",
    "overclaimed": "存在过度外推",
    "insufficient": "证据不足",
    "not_applicable": "不适用",
    "high": "高",
    "medium": "中",
    "low": "低",
    "unclear": "暂不明确",
}

STATUS_LABELS = {
    "reported": "作者明确说明",
    "inferred": "基于论文分析",
    "unknown": "当前材料无法确认",
}

READING_PRIORITY_LABELS = {
    "must_read": "建议完整精读",
    "read_core_sections": "建议重点阅读核心章节",
    "skim": "建议快速浏览",
    "low_priority": "当前阅读优先级较低",
    "insufficient_evidence": "材料不足，暂不建议据此判断",
}

COVERAGE_LABELS = {
    "sufficient": "充分",
    "partial": "部分",
    "limited": "有限",
}

LOCATOR_LABELS = {
    "page_grounded": "可定位至 PDF 页码及章节/图表",
    "structure_grounded": "可定位至章节/图表",
    "source_limited": "仅能定位至有限材料来源",
}

CONTEXT_LABELS = {
    "paper_only": "仅基于本文",
    "targeted_external_check": "已做定向外部核验",
    "externally_verified": "已做外部核验",
}

EXTERNAL_VERIFICATION_LABELS = {
    "not_checked": "未进行外部复现/核验",
    "not_applicable": "不适用",
    "partially_verified": "部分外部核验",
    "verified": "已外部核验",
    "conflicted": "外部证据存在冲突",
}

NOVELTY_STATUS_LABELS = {
    "paper_only": "仅完成论文内部比较",
    "not_externally_verified": "尚未进行外部文献核验",
    "targeted_external_check": "已完成定向外部文献核验",
    "externally_verified": "已完成外部文献核验",
}

ORIGIN_LABELS = {
    "author_stated": "作者提出",
    "analysis_derived": "PaperScope 分析得到",
    "reported": "作者提出",
    "inferred": "PaperScope 分析得到",
}


EVIDENCE_TYPE_LABELS = {
    "title": "标题",
    "metadata": "元数据",
    "abstract": "摘要",
    "body_text": "正文",
    "figure": "图",
    "table": "表格",
    "equation": "公式",
    "appendix": "附录",
    "supplement": "补充材料",
    "external_context": "外部资料",
}

EVIDENCE_GRADE_LABELS = {
    "E0_TITLE_METADATA": "仅标题与元数据",
    "E1_ABSTRACT": "摘要级材料",
    "E2_BODY_TEXT": "正文级材料",
    "E3_BODY_PLUS_ARTIFACTS": "正文 + 图表/公式等材料",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        for key in ("text", "question", "one_sentence_takeaway"):
            if key in value:
                return _text(value.get(key))
    return str(value)


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _statement_text(stmt: Any) -> str:
    return _text(stmt).strip()


def _statement_status(stmt: Any) -> str | None:
    if isinstance(stmt, dict):
        return stmt.get("status") or stmt.get("claim_status")
    return None


def _statement_refs(stmt: Any) -> List[str]:
    if isinstance(stmt, dict):
        return [str(x) for x in (stmt.get("evidence_refs") or [])]
    return []


def _support_value(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("level") or value.get("rating")
    if value is None:
        return ""
    raw = str(value)
    return LEVEL_LABELS.get(raw, raw)


def _status_value(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value)
    return STATUS_LABELS.get(raw, raw)


def _locator(ev: Dict[str, Any]) -> str:
    loc = ev.get("location") or {}
    mode = ev.get("locator_mode")
    parts: List[str] = []
    if loc.get("section"):
        parts.append(str(loc["section"]))
    if mode == "page_grounded" and loc.get("page"):
        parts.append(f"PDF p. {loc['page']}")
    if loc.get("figure"):
        parts.append(str(loc["figure"]))
    if loc.get("table"):
        parts.append(str(loc["table"]))
    if loc.get("equation"):
        parts.append(str(loc["equation"]))
    if not parts:
        src = ev.get("source") or ev.get("source_label") or ev.get("source_type")
        if src:
            parts.append(str(src))
    return " · ".join(parts) or "位置未提供"


def _presentation(style: Dict[str, Any] | None) -> Dict[str, Any]:
    style = style or {}
    defaults = {
        "humanize_enums": True,
        "show_status_labels": False,
        "show_technical_metadata": False,
        "evidence_mode": "inline_first",
        "evidence_index": True,
    }
    defaults.update(style.get("presentation") or {})
    return defaults


@dataclass
class EvidencePresenter:
    ev_map: Dict[str, Dict[str, Any]]
    mode: str = "inline_first"
    shown: Set[str] = field(default_factory=set)
    used: List[str] = field(default_factory=list)

    def _remember(self, ref_id: str):
        if ref_id not in self.used:
            self.used.append(ref_id)

    def compact_label(self, ref_ids: List[str]) -> str:
        valid = [r for r in ref_ids if r in self.ev_map]
        for r in valid:
            self._remember(r)
        return "、".join(valid)

    def callouts(self, ref_ids: List[str]) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = []
        for ref_id in ref_ids:
            ev = self.ev_map.get(ref_id)
            if not ev:
                continue
            self._remember(ref_id)
            if self.mode == "index_only":
                continue
            if self.mode == "inline_first" and ref_id in self.shown:
                continue
            self.shown.add(ref_id)

            snippet = ev.get("snippet")
            paraphrase = ev.get("paraphrase") or ev.get("note")
            verified = ev.get("verification_status") == "verified"
            if snippet:
                title = "原文依据" if verified else "材料片段"
                text = str(snippet)
                role = "evidence"
            elif paraphrase:
                title = "核验提示"
                text = str(paraphrase)
                role = "note"
            else:
                title = "依据定位"
                text = "已记录证据位置，但当前没有可直接展示的原文片段。"
                role = "note"

            meta = {"证据": ref_id, "位置": _locator(ev)}
            if ev.get("verification_status") == "needs_verification":
                meta["状态"] = "待核验"
            blocks.append({"type": "callout", "role": role, "title": title, "text": text, "meta": meta})
        return blocks

    def index_blocks(self) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = []
        for ref_id in self.used:
            ev = self.ev_map.get(ref_id)
            if not ev:
                continue
            snippet = ev.get("snippet")
            paraphrase = ev.get("paraphrase") or ev.get("note")
            if snippet:
                text = str(snippet)
                title = f"{ref_id} · 原文"
                role = "evidence"
            elif paraphrase:
                text = str(paraphrase)
                title = f"{ref_id} · 核验提示"
                role = "note"
            else:
                text = "当前没有可直接展示的原文片段。"
                title = f"{ref_id} · 依据定位"
                role = "note"
            meta = {"位置": _locator(ev)}
            if ev.get("evidence_type"):
                meta["证据类型"] = EVIDENCE_TYPE_LABELS.get(str(ev.get("evidence_type")), str(ev.get("evidence_type")))
            blocks.append({"type": "callout", "role": role, "title": title, "text": text, "meta": meta})
        return blocks


def _heading(blocks: List[Dict[str, Any]], text: str, level: int = 1):
    blocks.append({"type": "heading", "role": f"heading{min(level, 3)}", "level": level, "text": text})


def _add_statement(
    blocks: List[Dict[str, Any]],
    stmt: Any,
    evidence: EvidencePresenter,
    role: str = "body",
    label: str | None = None,
    show_status: bool = False,
):
    text = _statement_text(stmt)
    if not text:
        return
    status = _statement_status(stmt)
    prefix = f"{label}：" if label else ""
    if show_status and status:
        prefix += f"{_status_value(status)}｜"
    blocks.append({"type": "paragraph", "role": role, "text": prefix + text})
    blocks.extend(evidence.callouts(_statement_refs(stmt)))


def _research_value_rows(value: Any) -> List[List[str]]:
    rows: List[List[str]] = []
    if not isinstance(value, dict):
        return rows
    labels = {"methodological": "方法学价值", "empirical": "实证价值", "application": "应用价值"}
    for key, label in labels.items():
        v = value.get(key)
        if isinstance(v, dict):
            rows.append([label, _support_value(v.get("level") or v.get("rating")), _text(v.get("rationale") or v.get("reason"))])
        elif v is not None:
            rows.append([label, _support_value(v), ""])
    return rows


def _source_boundary_meta(paper: Dict[str, Any], technical: bool) -> Dict[str, Any]:
    sb = paper.get("source_boundary") or {}
    coverage = sb.get("evidence_coverage") or {}
    if not isinstance(coverage, dict):
        coverage = {"level": coverage}
    meta: Dict[str, Any] = {}
    level = coverage.get("level") or sb.get("coverage")
    if level:
        meta["材料覆盖"] = COVERAGE_LABELS.get(str(level), str(level))
    locator = sb.get("locator_mode")
    if locator:
        meta["证据定位"] = LOCATOR_LABELS.get(str(locator), str(locator))
    context = sb.get("context_mode")
    if context:
        meta["外部核验"] = CONTEXT_LABELS.get(str(context), str(context))
    if technical:
        grade = sb.get("evidence_grade") or paper.get("evidence_grade")
        if grade:
            meta["Evidence Grade"] = str(grade)
    return meta


def _paper_identity_meta(paper: Dict[str, Any], technical: bool = False) -> Dict[str, Any]:
    identity = paper.get("identity") or {}
    meta: Dict[str, Any] = {}
    if identity.get("authors"):
        meta["作者"] = ", ".join(identity.get("authors") or [])
    if identity.get("venue"):
        meta["期刊/会议"] = identity.get("venue")
    if identity.get("year"):
        meta["年份"] = identity.get("year")
    if identity.get("doi"):
        meta["DOI"] = identity.get("doi")
    if identity.get("arxiv"):
        meta["arXiv"] = identity.get("arxiv")
    if identity.get("version_note"):
        meta["分析版本"] = identity.get("version_note")
    meta.update(_source_boundary_meta(paper, technical))
    return meta


def _method_diff_table(method: Dict[str, Any], evidence: EvidencePresenter, show_status: bool) -> Dict[str, Any] | None:
    rows: List[List[str]] = []
    for key, label in [
        ("previous_approach", "Previous"),
        ("proposed_change", "Proposed"),
        ("mechanism", "Mechanism"),
        ("expected_benefit", "Expected Effect"),
    ]:
        stmt = method.get(key)
        text = _statement_text(stmt)
        if not text:
            continue
        status = _statement_status(stmt)
        if show_status and status:
            text = f"{_status_value(status)}｜{text}"
        refs = _statement_refs(stmt)
        ref_label = evidence.compact_label(refs)
        if ref_label:
            text += f"\n依据：{ref_label}"
        rows.append([label, text])
    if not rows:
        return None
    return {"type": "table", "role": "table", "caption": "Method Diff", "headers": ["环节", "内容"], "rows": rows}


def _adapt_one_paper(paper: Dict[str, Any], style: Dict[str, Any] | None, index: int = 0, multi: bool = False) -> tuple[List[Dict[str, Any]], EvidencePresenter]:
    blocks: List[Dict[str, Any]] = []
    p_opts = _presentation(style)
    ev_map = {str(ev.get("id")): ev for ev in _as_list(paper.get("evidence_refs")) if isinstance(ev, dict) and ev.get("id")}
    evidence = EvidencePresenter(ev_map=ev_map, mode=str(p_opts.get("evidence_mode", "inline_first")))
    show_status = bool(p_opts.get("show_status_labels", False))

    identity = paper.get("identity") or {}
    paper_title = identity.get("title") or f"论文 {index + 1}"
    if multi:
        if index:
            blocks.append({"type": "page_break", "role": "body"})
        _heading(blocks, paper_title, 1)

    # 01 Overview
    _heading(blocks, "01 论文速览", 1 if not multi else 2)
    jc = paper.get("judgment_card") or {}
    takeaway = jc.get("one_sentence_takeaway")
    if takeaway:
        blocks.append({"type": "callout", "role": "analysis", "title": "一句话看懂", "text": str(takeaway)})

    overview_rows: List[List[str]] = []
    strength = jc.get("paper_internal_evidence_strength") or jc.get("evidence_strength")
    if strength:
        overview_rows.append(["论文内部证据支持", _support_value(strength)])
    rp = jc.get("reading_priority")
    if isinstance(rp, dict):
        overview_rows.append(["阅读优先级", READING_PRIORITY_LABELS.get(str(rp.get("level")), str(rp.get("level", "")))])
        if rp.get("reason"):
            overview_rows.append(["阅读建议", str(rp.get("reason"))])
    elif rp:
        overview_rows.append(["阅读优先级", READING_PRIORITY_LABELS.get(str(rp), str(rp))])
    if jc.get("who_should_read"):
        overview_rows.append(["适合读者", "；".join(str(x) for x in (jc.get("who_should_read") or []))])
    if overview_rows:
        blocks.append({"type": "table", "role": "table", "headers": ["项目", "判断"], "rows": overview_rows})

    rv_rows = _research_value_rows(jc.get("research_value"))
    if rv_rows:
        blocks.append({"type": "table", "role": "table", "caption": "研究价值", "headers": ["维度", "等级", "理由"], "rows": rv_rows})

    # 02 Problem & Gap
    _heading(blocks, "02 研究问题与 Gap", 1 if not multi else 2)
    rp_obj = paper.get("research_problem")
    if isinstance(rp_obj, dict):
        _add_statement(blocks, rp_obj.get("author_framing"), evidence, label="作者表述", show_status=show_status)
        _add_statement(blocks, rp_obj.get("actual_problem"), evidence, role="analysis", label="PaperScope 判断的实际问题", show_status=show_status)
        _add_statement(blocks, rp_obj.get("claimed_gap"), evidence, label="论文声称的 Gap", show_status=show_status)
        _add_statement(blocks, rp_obj.get("gap_assessment"), evidence, role="analysis", label="Gap 判断", show_status=show_status)
    else:
        _add_statement(blocks, paper.get("research_question"), evidence, label="研究问题", show_status=show_status)

    # 03 Method & novelty
    _heading(blocks, "03 核心方法与真实创新", 1 if not multi else 2)
    method = paper.get("method_summary") or {}
    _add_statement(blocks, method.get("summary"), evidence, role="lead", label="方法概述", show_status=show_status)
    diff_table = _method_diff_table(method, evidence, show_status)
    if diff_table:
        blocks.append(diff_table)

    modules = method.get("main_modules") or method.get("modules") or []
    if modules:
        _heading(blocks, "核心模块", 2 if not multi else 3)
        for i, module in enumerate(modules, 1):
            if isinstance(module, dict) and module.get("module_name"):
                _heading(blocks, f"{i}. {module.get('module_name')}", 3)
                rows: List[List[str]] = []
                for k, label in [
                    ("purpose", "作用"), ("input", "输入"), ("operation", "操作"),
                    ("output", "输出"), ("why_needed", "为什么需要"), ("measured_effect", "已测得影响")
                ]:
                    if module.get(k):
                        rows.append([label, _text(module.get(k))])
                refs = [str(x) for x in module.get("evidence_refs", [])]
                if refs:
                    rows.append(["依据", evidence.compact_label(refs)])
                if rows:
                    blocks.append({"type": "table", "role": "table", "headers": ["项目", "内容"], "rows": rows})
                blocks.extend(evidence.callouts(refs))
            else:
                _add_statement(blocks, module, evidence, label=f"模块 {i}", show_status=show_status)

    assumptions = method.get("assumptions") or []
    if assumptions:
        _heading(blocks, "关键假设", 2 if not multi else 3)
        for i, a in enumerate(assumptions, 1):
            if not isinstance(a, dict):
                blocks.append({"type": "paragraph", "role": "body", "text": f"A{i} {a}"})
                continue
            aid = a.get("assumption_id") or f"A{i}"
            atext = a.get("assumption_text") or a.get("text") or ""
            provenance = a.get("provenance") or ""
            risk = a.get("risk_level") or ""
            lines = [str(atext)]
            if provenance:
                lines.append("来源性质：" + ("作者明确假设" if provenance == "explicit" else "隐含假设" if provenance == "inferred" else str(provenance)))
            if risk:
                lines.append("风险等级：" + LEVEL_LABELS.get(str(risk), str(risk)))
            if a.get("failure_mode") or a.get("risk_note"):
                lines.append("若不成立：" + str(a.get("failure_mode") or a.get("risk_note")))
            if a.get("testability"):
                lines.append("如何检验：" + str(a.get("testability")))
            refs = [str(x) for x in a.get("evidence_refs", [])]
            if refs:
                lines.append("依据：" + evidence.compact_label(refs))
            blocks.append({"type": "callout", "role": "warning" if risk == "high" else "analysis", "title": f"假设 {aid}", "text": "\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    novelty = paper.get("novelty_verification") or paper.get("novelty")
    if isinstance(novelty, dict):
        _heading(blocks, "创新判断", 2 if not multi else 3)
        delta = novelty.get("paper_relative_delta")
        if delta:
            if isinstance(delta, dict):
                _add_statement(blocks, delta, evidence, role="analysis", label="相对本文 prior work 的变化", show_status=show_status)
            else:
                blocks.append({"type": "paragraph", "role": "analysis", "text": "相对本文 prior work 的变化：" + _text(delta)})
        field_novelty = novelty.get("field_novelty")
        status = novelty.get("status") or novelty.get("verification_status")
        if field_novelty:
            if isinstance(field_novelty, dict):
                _add_statement(blocks, field_novelty, evidence, role="analysis", label="领域创新核验", show_status=show_status)
            else:
                blocks.append({"type": "paragraph", "role": "analysis", "text": "领域创新核验：" + _text(field_novelty)})
        elif status in {"paper_only", "not_externally_verified"}:
            blocks.append({"type": "callout", "role": "note", "title": "领域首创性", "text": "当前未进行系统外部 prior-art 核验，因此不据此判断是否属于领域首次提出。"})
        if status:
            blocks.append({"type": "paragraph", "role": "note", "text": "核验状态：" + NOVELTY_STATUS_LABELS.get(str(status), str(status))})

    contributions = paper.get("contributions") or []
    if contributions:
        _heading(blocks, "主要贡献", 2 if not multi else 3)
        for i, c in enumerate(contributions, 1):
            _add_statement(blocks, c, evidence, label=f"贡献 {i}", show_status=show_status)

    # 04 Experiments & evidence
    _heading(blocks, "04 实验与证据", 1 if not multi else 2)
    findings = paper.get("evaluation_or_findings") or []
    if findings:
        _heading(blocks, "主要结果", 2 if not multi else 3)
        for i, f in enumerate(findings, 1):
            _add_statement(blocks, f, evidence, label=f"结果 {i}", show_status=show_status)

    claims = paper.get("claim_evidence") or []
    if claims:
        _heading(blocks, "Claim–Evidence", 2 if not multi else 3)
        for i, item in enumerate(claims, 1):
            if not isinstance(item, dict):
                continue
            claim = item.get("claim") or item.get("claim_text") or ""
            claim_text = _statement_text(claim) if isinstance(claim, dict) else _text(claim)
            refs = [str(x) for x in (item.get("evidence_refs") or _statement_refs(claim))]
            support = item.get("paper_internal_support") or item.get("support_strength")
            ext = item.get("external_verification_status")
            rows = [
                ["核心判断", claim_text],
                ["论文内部支持", _support_value(support)],
                ["为什么", _text(item.get("support_reason"))],
                ["适用边界", _text(item.get("scope_boundary"))],
                ["不能进一步证明", _text(item.get("unsupported_stronger_claim"))],
                ["如何进一步加强", _text(item.get("what_would_strengthen_it"))],
                ["外部核验", EXTERNAL_VERIFICATION_LABELS.get(str(ext), str(ext)) if ext else ""],
                ["依据", evidence.compact_label(refs)],
            ]
            rows = [[k, v] for k, v in rows if v not in (None, "")]
            claim_id = item.get("claim_id") or f"Claim {i}"
            blocks.append({"type": "table", "role": "table", "caption": str(claim_id), "headers": ["项目", "内容"], "rows": rows})
            blocks.extend(evidence.callouts(refs))

    audit = paper.get("evidence_audit") or {}
    if audit:
        overall = audit.get("paper_internal_support") or audit.get("overall_support")
        if overall:
            blocks.append({"type": "callout", "role": "analysis", "title": "整体论文内部证据支持", "text": _support_value(overall)})
        ext = audit.get("external_verification_status")
        if ext:
            blocks.append({"type": "paragraph", "role": "note", "text": "外部核验状态：" + EXTERNAL_VERIFICATION_LABELS.get(str(ext), str(ext))})
        for key, label, role in [
            ("strongly_supported", "支持较充分的判断", "analysis"),
            ("weakly_supported", "支持有限的判断", "warning"),
            ("unsupported_or_overclaimed", "证据不足或可能过度外推", "limitation"),
        ]:
            vals = audit.get(key) or []
            if vals:
                _heading(blocks, label, 3)
                for v in vals:
                    _add_statement(blocks, v, evidence, role=role, show_status=show_status)
        missing = audit.get("missing_evidence") or []
        if missing:
            _heading(blocks, "仍缺少的验证", 3)
            blocks.append({"type": "list", "role": "warning", "ordered": False, "items": [str(x) for x in missing]})

    # 05 Critical review
    _heading(blocks, "05 批判性评价", 1 if not multi else 2)
    author_limits = paper.get("author_acknowledged_limitations") or []
    if author_limits:
        _heading(blocks, "作者明确指出的局限 / 约束", 2 if not multi else 3)
        for item in author_limits:
            _add_statement(blocks, item, evidence, role="limitation", show_status=show_status)

    unknowns = paper.get("unresolved_unknowns") or []
    if unknowns:
        _heading(blocks, "当前材料仍无法确认", 2 if not multi else 3)
        blocks.append({"type": "list", "role": "note", "ordered": False, "items": [str(x) for x in unknowns]})

    # v1.2 compatibility
    legacy_limits = paper.get("limitations_or_unknowns") or []
    if legacy_limits and not author_limits:
        _heading(blocks, "局限与未知", 2 if not multi else 3)
        for item in legacy_limits:
            _add_statement(blocks, item, evidence, role="limitation", show_status=show_status)

    crit = paper.get("critical_review") or {}
    analysis_limits = crit.get("analysis_limitations") or crit.get("main_limitations") or []
    if analysis_limits:
        _heading(blocks, "PaperScope 分析出的局限", 2 if not multi else 3)
        for item in analysis_limits:
            _add_statement(blocks, item, evidence, role="limitation", show_status=show_status)

    fragile = crit.get("fragile_assumptions") or []
    if fragile:
        _heading(blocks, "脆弱假设", 2 if not multi else 3)
        for i, item in enumerate(fragile, 1):
            if not isinstance(item, dict):
                continue
            aid = item.get("assumption_id") or f"A{i}"
            failure = item.get("failure_mode") or ""
            refs = [str(x) for x in item.get("evidence_refs", [])]
            lines = ["若该假设不成立：" + str(failure)]
            if refs:
                lines.append("依据：" + evidence.compact_label(refs))
            blocks.append({"type": "callout", "role": "warning", "title": f"脆弱假设 {aid}", "text": "\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    questions = crit.get("reviewer_questions") or []
    if questions:
        _heading(blocks, "Reviewer Questions", 2 if not multi else 3)
        blocks.append({"type": "list", "role": "warning", "ordered": True, "items": [str(x) for x in questions[:5]]})

    repro = crit.get("reproducibility_risks") or []
    if repro:
        _heading(blocks, "复现风险", 3)
        blocks.append({"type": "list", "role": "warning", "ordered": False, "items": [str(x) for x in repro]})

    eval_risks = crit.get("evaluation_risks") or []
    if eval_risks:
        _heading(blocks, "评估风险", 3)
        blocks.append({"type": "list", "role": "warning", "ordered": False, "items": [str(x) for x in eval_risks]})

    applicability = crit.get("applicability_boundary") or []
    if applicability:
        _heading(blocks, "适用边界", 3)
        for item in applicability:
            _add_statement(blocks, item, evidence, role="analysis", show_status=show_status)

    contradictions = paper.get("contradictions") or []
    if contradictions:
        _heading(blocks, "材料中的不一致", 2 if not multi else 3)
        for item in contradictions:
            if not isinstance(item, dict):
                continue
            refs = [str(x) for x in (item.get("evidence_refs") or [])]
            lines = [str(item.get("description") or "发现材料不一致")]
            if item.get("impact"):
                lines.append("影响：" + str(item.get("impact")))
            if item.get("resolution_needed"):
                lines.append("如何解决：" + str(item.get("resolution_needed")))
            if refs:
                lines.append("涉及证据：" + evidence.compact_label(refs))
            blocks.append({"type": "callout", "role": "warning", "title": "材料不一致", "text": "\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    # 06 Open questions & reading guide
    _heading(blocks, "06 开放问题与精读建议", 1 if not multi else 2)
    oqs = paper.get("open_questions") or []
    if oqs:
        _heading(blocks, "开放问题", 2 if not multi else 3)
        for i, q in enumerate(oqs, 1):
            if not isinstance(q, dict):
                blocks.append({"type": "paragraph", "role": "analysis", "text": str(q)})
                continue
            refs = [str(x) for x in q.get("evidence_refs", [])]
            lines = ["问题：" + str(q.get("question") or "")]
            origin = q.get("origin") or q.get("status")
            if origin:
                lines.append("来源：" + ORIGIN_LABELS.get(str(origin), str(origin)))
            if q.get("why_it_matters"):
                lines.append("为什么重要：" + str(q.get("why_it_matters")))
            nxt = q.get("suggested_validation") or q.get("suggested_next_step")
            if nxt:
                lines.append("建议如何验证：" + str(nxt))
            if refs:
                lines.append("依据：" + evidence.compact_label(refs))
            blocks.append({"type": "callout", "role": "analysis", "title": f"Open Question {i}", "text": "\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    guide = paper.get("reading_guide") or {}
    if isinstance(guide, dict) and (guide.get("items") or guide.get("twenty_minute_path")):
        _heading(blocks, "精读路线", 2 if not multi else 3)
        items = guide.get("items") or []
        if items:
            rows: List[List[str]] = []
            pri_labels = {"must_read": "必读", "recommended": "推荐", "skim": "略读"}
            for item in items:
                if not isinstance(item, dict):
                    continue
                refs = [str(x) for x in item.get("evidence_refs", [])]
                rows.append([
                    pri_labels.get(str(item.get("priority")), str(item.get("priority") or "")),
                    str(item.get("target_label") or ""),
                    str(item.get("reason") or ""),
                    evidence.compact_label(refs),
                ])
            if rows:
                blocks.append({"type": "table", "role": "table", "headers": ["优先级", "原文位置", "为什么值得看", "依据"], "rows": rows})
        path = guide.get("twenty_minute_path") or []
        if path:
            blocks.append({"type": "callout", "role": "note", "title": "20 分钟阅读路线", "text": " → ".join(str(x) for x in path)})

    return blocks, evidence


def adapt(data: Dict[str, Any], style: Dict[str, Any] | None = None) -> Dict[str, Any]:
    papers = data.get("papers") or []
    if not papers:
        raise ValueError("Deep-reading result contains no papers.")

    opts = _presentation(style)
    first = papers[0]
    first_identity = first.get("identity") or {}
    base_title = first_identity.get("title") or "未命名论文"
    multi = len(papers) > 1

    title = "AI 论文精读报告"
    subtitle = f"{len(papers)} 篇论文综合精读" if multi else base_title

    metadata = _paper_identity_meta(first, technical=bool(opts.get("show_technical_metadata", False)))
    if multi:
        metadata["论文数量"] = len(papers)
    if opts.get("show_technical_metadata"):
        if data.get("analysis_type"):
            metadata["分析类型"] = data.get("analysis_type")
        if data.get("schema_version"):
            metadata["精读 Schema"] = data.get("schema_version")

    blocks: List[Dict[str, Any]] = []
    presenters: List[EvidencePresenter] = []
    for i, paper in enumerate(papers):
        one_blocks, presenter = _adapt_one_paper(paper, style, i, multi)
        blocks.extend(one_blocks)
        presenters.append(presenter)

    global_limits = data.get("global_limitations") or []
    if global_limits:
        _heading(blocks, "材料边界与说明", 1)
        blocks.append({"type": "list", "role": "note", "ordered": False, "items": [str(x) for x in global_limits]})

    if opts.get("evidence_index", True):
        index_blocks: List[Dict[str, Any]] = []
        for presenter in presenters:
            index_blocks.extend(presenter.index_blocks())
        if index_blocks:
            _heading(blocks, "附录：证据索引", 1)
            blocks.extend(index_blocks)

    return {
        "schema_version": "1.0",
        "document_id": f"deep-reading-{first.get('paper_id', 'report')}",
        "document_kind": "ai_deep_reading",
        "language": "zh-CN",
        "title": title,
        "subtitle": subtitle,
        "metadata": metadata,
        "blocks": blocks,
    }

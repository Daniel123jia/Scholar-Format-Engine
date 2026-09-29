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

MATERIAL_STATUS_LABELS = {
    "available": "已获取",
    "partial": "部分解析",
    "missing": "未获取",
    "not_checked": "未核验",
    "not_applicable": "不适用",
}

EVIDENCE_ROLE_LABELS = {
    "problem_framing": "问题界定",
    "method_definition": "方法定义",
    "main_result": "主实验",
    "ablation": "消融实验",
    "robustness": "稳健性/敏感性",
    "qualitative": "定性证据",
    "author_interpretation": "作者解释",
    "limitation": "局限/约束",
    "assumption": "假设依据",
    "protocol": "实验协议",
    "external_context": "外部资料",
    "metadata": "元数据",
    "other": "其他",
}

SUPPORT_RELATION_LABELS = {
    "direct": "直接支持",
    "indirect": "间接支持",
    "context": "背景/上下文",
    "contradictory": "存在冲突",
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

    def display_id(self, ref_id: str) -> str:
        try:
            n = int(str(ref_id).split("-")[-1])
            return f"E{n}"
        except Exception:
            return str(ref_id)

    def compact_label(self, ref_ids: List[str]) -> str:
        valid = [r for r in ref_ids if r in self.ev_map]
        for r in valid:
            self._remember(r)
        return "、".join(self.display_id(r) for r in valid)

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

            meta = {"证据": self.display_id(ref_id), "位置": _locator(ev)}
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
                title = f"{self.display_id(ref_id)} · 原文"
                role = "evidence"
            elif paraphrase:
                text = str(paraphrase)
                title = f"{self.display_id(ref_id)} · 核验提示"
                role = "note"
            else:
                text = "当前没有可直接展示的原文片段。"
                title = f"{self.display_id(ref_id)} · 依据定位"
                role = "note"
            meta = {"位置": _locator(ev)}
            if ev.get("evidence_type"):
                meta["材料类型"] = EVIDENCE_TYPE_LABELS.get(str(ev.get("evidence_type")), str(ev.get("evidence_type")))
            if ev.get("evidence_role"):
                meta["证据性质"] = EVIDENCE_ROLE_LABELS.get(str(ev.get("evidence_role")), str(ev.get("evidence_role")))
            supported = ev.get("supported_claim_ids") or []
            if supported:
                meta["支持"] = "、".join(f"Claim {int(str(x).split('-')[-1])}" if str(x).split('-')[-1].isdigit() else str(x) for x in supported)
            blocks.append({"type": "callout", "role": role, "title": title, "text": text, "meta": meta, "id": f"evidence-{ref_id}"})
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
    if identity.get("analyzed_version_label"):
        meta["分析版本"] = identity.get("analyzed_version_label")
    elif identity.get("version_note"):
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


def _coverage_rows(paper: Dict[str, Any]) -> List[List[str]]:
    sb = paper.get("source_boundary") or {}
    matrix = sb.get("coverage_matrix") or {}
    labels = [
        ("body_text", "正文"), ("sections", "章节结构"), ("tables", "表格"),
        ("figures", "图"), ("equations", "公式"), ("appendix", "附录"),
        ("supplement", "Supplement"), ("code", "代码"), ("external_literature", "外部文献"),
    ]
    rows=[]
    for key,label in labels:
        item=matrix.get(key) or {}
        if not item:
            continue
        status=MATERIAL_STATUS_LABELS.get(str(item.get("status")),str(item.get("status") or ""))
        rows.append([label,status,str(item.get("note") or "")])
    return rows


def _claim_refs(item: Dict[str, Any]) -> List[str]:
    if item.get("evidence_links"):
        return [str(x.get("evidence_id")) for x in item.get("evidence_links") or [] if isinstance(x,dict) and x.get("evidence_id")]
    return [str(x) for x in (item.get("evidence_refs") or [])]


def _claim_relation_text(item: Dict[str, Any], evidence: EvidencePresenter) -> str:
    parts=[]
    for link in item.get("evidence_links") or []:
        if not isinstance(link,dict) or not link.get("evidence_id"):
            continue
        eid=str(link.get("evidence_id"))
        rel=SUPPORT_RELATION_LABELS.get(str(link.get("relation")),str(link.get("relation") or ""))
        note=str(link.get("note") or "")
        text=f"{evidence.display_id(eid)}（{rel}）"
        if note:
            text+=f"：{note}"
        parts.append(text)
    return "；".join(parts)


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
    if jc.get("one_sentence_takeaway"):
        blocks.append({"type":"callout","role":"analysis","title":"一句话看懂","text":str(jc.get("one_sentence_takeaway"))})

    sig_rows=[]
    for key,label in [
        ("core_problem","核心问题"),("core_method","核心方法"),("paper_relative_innovation","真正变化"),
        ("strongest_evidence","最强证据"),("biggest_risk","最大风险"),("most_important_open_question","最重要开放问题")
    ]:
        if jc.get(key): sig_rows.append([label,str(jc.get(key))])
    if jc.get("key_assumptions"):
        sig_rows.append(["关键假设","；".join(str(x) for x in jc.get("key_assumptions") or [])])
    if sig_rows:
        blocks.append({"type":"table","role":"table","caption":"科研判断卡","headers":["项目","判断"],"rows":sig_rows,"column_widths_pct":[22,78]})

    overview_rows=[]
    strength=jc.get("paper_internal_evidence_strength") or jc.get("evidence_strength")
    if strength: overview_rows.append(["论文内部证据支持",_support_value(strength)])
    rp=jc.get("reading_priority")
    if isinstance(rp,dict):
        overview_rows.append(["阅读优先级",READING_PRIORITY_LABELS.get(str(rp.get("level")),str(rp.get("level", "")))])
        if rp.get("reason"): overview_rows.append(["理由",str(rp.get("reason"))])
    elif rp: overview_rows.append(["阅读优先级",READING_PRIORITY_LABELS.get(str(rp),str(rp))])
    if jc.get("who_should_read"): overview_rows.append(["适合读者","；".join(str(x) for x in jc.get("who_should_read") or [])])
    if overview_rows:
        blocks.append({"type":"table","role":"table","headers":["项目","判断"],"rows":overview_rows,"column_widths_pct":[24,76]})
    rv_rows=_research_value_rows(jc.get("research_value"))
    if rv_rows:
        blocks.append({"type":"table","role":"table","caption":"研究价值","headers":["维度","等级","理由"],"rows":rv_rows,"column_widths_pct":[18,12,70]})

    coverage_rows=_coverage_rows(paper)
    if coverage_rows:
        _heading(blocks,"材料覆盖",2 if not multi else 3)
        blocks.append({"type":"table","role":"table","headers":["材料","状态","说明"],"rows":coverage_rows,"column_widths_pct":[18,18,64]})

    # 02 Research problem and Gap
    _heading(blocks, "02 研究问题与 Gap", 1 if not multi else 2)
    _add_statement(blocks,paper.get("research_question"),evidence,label="研究问题",show_status=show_status)
    gap=paper.get("research_gap") or {}
    if gap:
        _add_statement(blocks,gap.get("author_problem"),evidence,label="作者界定的问题",show_status=show_status)
        _add_statement(blocks,gap.get("author_claimed_gap"),evidence,label="论文声称的 Gap",show_status=show_status)
        _add_statement(blocks,gap.get("paperscope_bottleneck"),evidence,role="analysis",label="PaperScope 判断的实际瓶颈",show_status=show_status)
        ga=gap.get("gap_assessment") or {}
        if ga:
            status_map={"established":"Gap 基本成立","partially_established":"Gap 部分成立","narrative_overreach":"存在一定叙事放大","unclear":"当前材料不足以判断"}
            refs=[str(x) for x in ga.get("evidence_refs") or []]
            text=status_map.get(str(ga.get("status")),str(ga.get("status") or ""))
            if ga.get("rationale"): text += "。"+str(ga.get("rationale"))
            if refs: text += "\n依据："+evidence.compact_label(refs)
            blocks.append({"type":"callout","role":"analysis","title":"Gap 判断","text":text})
            blocks.extend(evidence.callouts(refs))

    # 03 Method and innovation
    _heading(blocks, "03 核心方法与真实创新", 1 if not multi else 2)
    method=paper.get("method_summary") or {}
    _add_statement(blocks,method.get("summary"),evidence,role="lead",label="方法概述",show_status=show_status)
    diff=_method_diff_table(method,evidence,show_status)
    if diff:
        diff["caption"]="方法差异链（Method Diff）"
        diff["column_widths_pct"]=[23,77]
        blocks.append(diff)

    modules=method.get("main_modules") or method.get("modules") or []
    if modules:
        _heading(blocks,"核心模块",2 if not multi else 3)
        rows=[]
        for m in modules:
            if not isinstance(m,dict): continue
            refs=[str(x) for x in m.get("evidence_refs") or []]
            rows.append([
                str(m.get("module_name") or ""),str(m.get("purpose") or ""),str(m.get("input") or ""),
                str(m.get("operation") or ""),str(m.get("output") or ""),str(m.get("why_needed") or ""),evidence.compact_label(refs)
            ])
        if rows:
            blocks.append({"type":"table","role":"table","headers":["模块","作用","输入","操作","输出","为什么需要","依据"],"rows":rows,"column_widths_pct":[12,14,12,22,12,20,8]})

    equations=method.get("key_equations") or []
    if equations:
        _heading(blocks,"关键公式 / 定理",2 if not multi else 3)
        for eq in equations:
            if not isinstance(eq,dict): continue
            refs=[str(x) for x in eq.get("evidence_refs") or []]
            lines=["作用："+str(eq.get("purpose") or ""),"直觉："+str(eq.get("intuition") or "")]
            syms=eq.get("symbols") or []
            if syms: lines.append("符号："+"；".join(f"{x.get('symbol')}={x.get('meaning')}" for x in syms if isinstance(x,dict)))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"analysis","title":str(eq.get("label") or "关键公式"),"text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    assumptions=method.get("assumptions") or []
    if assumptions:
        _heading(blocks,"关键假设",2 if not multi else 3)
        for i,a in enumerate(assumptions,1):
            if not isinstance(a,dict): continue
            aid=a.get("assumption_id") or f"A{i}"
            display_aid=f"A{i}"
            risk=a.get("risk_level") or ""
            refs=[str(x) for x in a.get("evidence_refs") or []]
            lines=[str(a.get("assumption_text") or "")]
            prov=a.get("provenance")
            if prov: lines.append("来源性质："+("作者明确假设" if prov=="explicit" else "隐含假设" if prov=="inferred" else str(prov)))
            if risk: lines.append("风险等级："+LEVEL_LABELS.get(str(risk),str(risk)))
            if a.get("why_needed"): lines.append("为什么需要："+str(a.get("why_needed")))
            if a.get("failure_mode"): lines.append("若不成立："+str(a.get("failure_mode")))
            if a.get("stress_test"): lines.append("如何压力测试："+str(a.get("stress_test")))
            elif a.get("testability"): lines.append("如何检验："+str(a.get("testability")))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"warning" if risk=="high" else "analysis","title":f"假设 {display_aid}","text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    novelty=paper.get("novelty_verification") or {}
    if novelty:
        _heading(blocks,"创新判断",2 if not multi else 3)
        delta=novelty.get("paper_relative_delta")
        if delta:
            if isinstance(delta,dict): _add_statement(blocks,delta,evidence,role="analysis",label="相对本文 prior work 的变化",show_status=show_status)
            else: blocks.append({"type":"paragraph","role":"analysis","text":"相对本文 prior work 的变化："+_text(delta)})
        field=novelty.get("field_novelty")
        status=novelty.get("status")
        if field:
            if isinstance(field,dict): _add_statement(blocks,field,evidence,role="analysis",label="领域首创性",show_status=show_status)
            else: blocks.append({"type":"paragraph","role":"analysis","text":"领域首创性："+_text(field)})
        else:
            blocks.append({"type":"callout","role":"note","title":"领域首创性","text":"未进行系统外部文献核验，暂不判断是否属于领域首次提出。"})
        if status: blocks.append({"type":"paragraph","role":"note","text":"核验状态："+NOVELTY_STATUS_LABELS.get(str(status),str(status))})

    contributions=paper.get("contributions") or []
    if contributions:
        _heading(blocks,"主要贡献",2 if not multi else 3)
        for i,c in enumerate(contributions,1): _add_statement(blocks,c,evidence,label=f"贡献 {i}",show_status=show_status)

    # 04 Experiments and evidence
    _heading(blocks,"04 实验与证据",1 if not multi else 2)
    experiments=paper.get("experiments") or []
    if experiments:
        _heading(blocks,"实验解释链",2 if not multi else 3)
        for i,ex in enumerate(experiments,1):
            if not isinstance(ex,dict): continue
            refs=[str(x) for x in ex.get("evidence_refs") or []]
            lines=[
                "实验目的："+str(ex.get("purpose") or ""),
                "设计："+str(ex.get("design") or ""),
                "比较条件："+str(ex.get("comparison_conditions") or ""),
                "结果："+str(ex.get("result") or ""),
                "真正支持："+str(ex.get("supported_conclusion") or "")
            ]
            if ex.get("unsupported_stronger_conclusion"): lines.append("不能进一步证明："+str(ex.get("unsupported_stronger_conclusion")))
            if ex.get("protocol_risks"): lines.append("协议风险："+"；".join(str(x) for x in ex.get("protocol_risks") or []))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"analysis","title":f"实验 {i}","text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    findings=paper.get("evaluation_or_findings") or []
    if findings:
        _heading(blocks,"主要结果",2 if not multi else 3)
        for i,f in enumerate(findings,1): _add_statement(blocks,f,evidence,label=f"结果 {i}",show_status=show_status)

    claims=paper.get("claim_evidence") or []
    if claims:
        _heading(blocks,"Claim–Evidence",2 if not multi else 3)
        for i,item in enumerate(claims,1):
            if not isinstance(item,dict): continue
            claim=item.get("claim") or {}
            claim_text=_statement_text(claim) if isinstance(claim,dict) else _text(claim)
            refs=_claim_refs(item)
            support=item.get("paper_internal_support") or item.get("support_strength")
            ext=item.get("external_verification_status")
            lines=[
                "核心判断："+claim_text,
                "论文内部支持："+_support_value(support),
                "为什么："+_text(item.get("support_reason")),
            ]
            reltext=_claim_relation_text(item,evidence)
            if reltext: lines.append("证据关系："+reltext)
            if item.get("scope_boundary"): lines.append("适用边界："+_text(item.get("scope_boundary")))
            if item.get("unsupported_stronger_claim"): lines.append("不能进一步证明："+_text(item.get("unsupported_stronger_claim")))
            if item.get("what_would_strengthen_it"): lines.append("如何进一步加强："+_text(item.get("what_would_strengthen_it")))
            if ext: lines.append("外部核验："+EXTERNAL_VERIFICATION_LABELS.get(str(ext),str(ext)))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            claim_title=str(item.get("claim_title") or "").strip()
            visible_title=f"Claim {i}｜{claim_title}" if claim_title else f"Claim {i}"
            blocks.append({"type":"callout","role":"analysis","title":visible_title,"text":"\n".join(lines),"id":f"claim-{i}"})
            blocks.extend(evidence.callouts(refs))

    audit=paper.get("evidence_audit") or {}
    if audit:
        overall=audit.get("paper_internal_support") or audit.get("overall_support")
        if overall: blocks.append({"type":"callout","role":"analysis","title":"整体论文内部证据支持","text":_support_value(overall)})
        missing=audit.get("missing_evidence") or []
        if missing:
            _heading(blocks,"仍缺少的验证",3)
            blocks.append({"type":"list","role":"note","ordered":False,"items":[str(x) for x in missing]})

    # 05 Critical review
    _heading(blocks,"05 批判性评价",1 if not multi else 2)
    author_limits=paper.get("author_acknowledged_limitations") or []
    if author_limits:
        _heading(blocks,"作者明确指出的局限 / 约束",2 if not multi else 3)
        for item in author_limits: _add_statement(blocks,item,evidence,role="body",show_status=show_status)
    unknowns=paper.get("unresolved_unknowns") or []
    if unknowns:
        _heading(blocks,"当前材料仍无法确认",2 if not multi else 3)
        blocks.append({"type":"list","role":"note","ordered":False,"items":[str(x) for x in unknowns]})
    crit=paper.get("critical_review") or {}
    analysis_limits=crit.get("analysis_limitations") or []
    if analysis_limits:
        _heading(blocks,"PaperScope 分析出的局限",2 if not multi else 3)
        for item in analysis_limits: _add_statement(blocks,item,evidence,role="body",show_status=show_status)
    core_weaknesses=crit.get("core_weaknesses") or []
    if core_weaknesses:
        _heading(blocks,"PaperScope 判断的核心缺陷",2 if not multi else 3)
        claim_title_map={str(c.get("claim_id")):str(c.get("claim_title") or "") for c in claims if isinstance(c,dict) and c.get("claim_id")}
        assumption_index={str(a.get("assumption_id")):idx+1 for idx,a in enumerate(assumptions) if isinstance(a,dict) and a.get("assumption_id")}
        for i,w in enumerate(core_weaknesses,1):
            if not isinstance(w,dict): continue
            refs=[str(x) for x in w.get("evidence_refs") or []]
            lines=[]
            if w.get("description"): lines.append("缺陷是什么："+str(w.get("description")))
            if w.get("why_it_matters"): lines.append("为什么重要："+str(w.get("why_it_matters")))
            if w.get("potential_impact"): lines.append("潜在影响："+str(w.get("potential_impact")))
            if w.get("suggested_validation"): lines.append("如何验证："+str(w.get("suggested_validation")))
            related_claims=[]
            for cid in w.get("related_claim_ids") or []:
                ct=claim_title_map.get(str(cid))
                related_claims.append(ct or str(cid))
            if related_claims: lines.append("关联主张："+"；".join(related_claims))
            related_ass=[]
            for aid in w.get("related_assumption_ids") or []:
                idx=assumption_index.get(str(aid))
                related_ass.append(f"A{idx}" if idx else str(aid))
            if related_ass: lines.append("关联假设："+"、".join(related_ass))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            title=str(w.get("title") or "核心缺陷")
            blocks.append({"type":"callout","role":"limitation","title":f"核心缺陷 {i}｜{title}","text":"\n".join(lines),"id":f"weakness-{i}"})
            blocks.extend(evidence.callouts(refs))

    fragile=crit.get("fragile_assumptions") or []
    if fragile:
        _heading(blocks,"脆弱假设",2 if not multi else 3)
        assumption_map={a.get("assumption_id"):a for a in assumptions if isinstance(a,dict)}
        for i,item in enumerate(fragile,1):
            if not isinstance(item,dict): continue
            src=assumption_map.get(item.get("assumption_id"),{})
            refs=[str(x) for x in item.get("evidence_refs") or []]
            lines=[]
            if src.get("assumption_text"): lines.append(str(src.get("assumption_text")))
            if item.get("failure_mode"): lines.append("若不成立："+str(item.get("failure_mode")))
            if src.get("stress_test"): lines.append("建议压力测试："+str(src.get("stress_test")))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"warning","title":f"脆弱假设 A{i}","text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))
    questions=crit.get("reviewer_questions") or []
    if questions:
        _heading(blocks,"审稿人可能关注的问题（Reviewer Questions）",2 if not multi else 3)
        blocks.append({"type":"list","role":"body","ordered":True,"items":[str(x) for x in questions[:3]]})
    for key,label in [("reproducibility_risks","复现风险"),("evaluation_risks","评估风险")]:
        vals=crit.get(key) or []
        if vals:
            _heading(blocks,label,3)
            blocks.append({"type":"list","role":"body","ordered":False,"items":[str(x) for x in vals]})
    applicability=crit.get("applicability_boundary") or []
    if applicability:
        _heading(blocks,"适用边界",3)
        for item in applicability: _add_statement(blocks,item,evidence,role="analysis",show_status=show_status)
    contradictions=paper.get("contradictions") or []
    if contradictions:
        _heading(blocks,"材料中的不一致",2 if not multi else 3)
        for item in contradictions:
            refs=[str(x) for x in item.get("evidence_refs") or []]
            lines=[str(item.get("description") or "发现材料不一致")]
            if item.get("impact"): lines.append("影响："+str(item.get("impact")))
            if item.get("resolution_needed"): lines.append("如何解决："+str(item.get("resolution_needed")))
            if refs: lines.append("涉及证据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"warning","title":"材料不一致","text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    # 06 Open questions and guided reading
    _heading(blocks,"06 开放问题与精读建议",1 if not multi else 2)
    oqs=paper.get("open_questions") or []
    if oqs:
        _heading(blocks,"开放问题",2 if not multi else 3)
        for i,q in enumerate(oqs,1):
            if not isinstance(q,dict): continue
            refs=[str(x) for x in q.get("evidence_refs") or []]
            lines=["问题："+str(q.get("question") or "")]
            if q.get("origin"): lines.append("来源："+ORIGIN_LABELS.get(str(q.get("origin")),str(q.get("origin"))))
            if q.get("why_it_matters"): lines.append("为什么重要："+str(q.get("why_it_matters")))
            if q.get("suggested_validation"): lines.append("建议如何验证："+str(q.get("suggested_validation")))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            blocks.append({"type":"callout","role":"analysis","title":f"Open Question {i}","text":"\n".join(lines)})
            blocks.extend(evidence.callouts(refs))

    directions=paper.get("research_directions") or []
    if directions:
        _heading(blocks,"后续研究方向（PaperScope 分析）",2 if not multi else 3)
        for i,rd in enumerate(directions,1):
            if not isinstance(rd,dict): continue
            refs=[str(x) for x in rd.get("evidence_refs") or []]
            lines=[]
            if rd.get("target_problem"): lines.append("目标问题："+str(rd.get("target_problem")))
            if rd.get("rationale"): lines.append("为什么值得继续："+str(rd.get("rationale")))
            if rd.get("validation_focus"): lines.append("优先验证："+str(rd.get("validation_focus")))
            if rd.get("boundary_note"): lines.append("边界说明："+str(rd.get("boundary_note")))
            if refs: lines.append("依据："+evidence.compact_label(refs))
            title=str(rd.get("title") or f"研究方向 {i}")
            blocks.append({"type":"callout","role":"research_direction","title":f"方向 {i}｜{title}","text":"\n".join(lines),"id":f"research-direction-{i}"})
            blocks.extend(evidence.callouts(refs))

    guide=paper.get("reading_guide") or {}
    if guide.get("items") or guide.get("twenty_minute_path"):
        _heading(blocks,"精读路线",2 if not multi else 3)
        rows=[]
        pri={"must_read":"必读","recommended":"推荐","skim":"略读"}
        for item in guide.get("items") or []:
            refs=[str(x) for x in item.get("evidence_refs") or []]
            rows.append([pri.get(str(item.get("priority")),str(item.get("priority") or "")),str(item.get("target_label") or ""),str(item.get("reason") or ""),evidence.compact_label(refs)])
        if rows:
            blocks.append({"type":"table","role":"table","headers":["优先级","原文位置","为什么值得看","依据"],"rows":rows,"column_widths_pct":[13,25,50,12]})
        path=guide.get("twenty_minute_path") or []
        if path:
            _heading(blocks,"20 分钟阅读路线",3)
            lines=[]
            for step in path:
                if isinstance(step,dict):
                    label=str(step.get("target_label") or "")
                    why=str(step.get("why_read") or "")
                    take=str(step.get("expected_takeaway") or "")
                    text=label
                    if why: text += "｜为什么看："+why
                    if take: text += "｜看完应得到："+take
                    lines.append(text)
                else:
                    lines.append(str(step))
            blocks.append({"type":"list","role":"analysis","ordered":True,"items":lines})

    return blocks,evidence

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
        "schema_version": "1.1",
        "document_id": f"deep-reading-{first.get('paper_id', 'report')}",
        "document_kind": "ai_deep_reading",
        "language": "zh-CN",
        "title": title,
        "subtitle": subtitle,
        "metadata": metadata,
        "blocks": blocks,
    }

from __future__ import annotations

from typing import Any, Dict, List


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        if "text" in value:
            return _text(value.get("text"))
        if "question" in value:
            return _text(value.get("question"))
        if "one_sentence_takeaway" in value:
            return _text(value.get("one_sentence_takeaway"))
    return str(value)


def _statement_text(stmt: Any) -> str:
    return _text(stmt).strip()


def _statement_status(stmt: Any) -> str | None:
    if isinstance(stmt, dict):
        return stmt.get("status") or stmt.get("claim_status")
    return None


def _statement_refs(stmt: Any) -> List[str]:
    if isinstance(stmt, dict):
        refs = stmt.get("evidence_refs") or []
        return [str(x) for x in refs]
    return []


def _locator(ev: Dict[str, Any]) -> str:
    loc = ev.get("location") or {}
    parts = []
    if loc.get("section"):
        parts.append(f"Section {loc['section']}")
    if loc.get("page"):
        parts.append(f"PDF p. {loc['page']}")
    if loc.get("figure"):
        parts.append(str(loc["figure"]))
    if loc.get("table"):
        parts.append(str(loc["table"]))
    if loc.get("equation"):
        parts.append(str(loc["equation"]))
    source = ev.get("source") or ev.get("source_label") or ev.get("source_type")
    if source and not parts:
        parts.append(str(source))
    return " · ".join(parts) or "位置未提供"


def _evidence_callouts(ref_ids: List[str], ev_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for ref_id in ref_ids:
        ev = ev_map.get(ref_id)
        if not ev:
            continue
        snippet = ev.get("snippet")
        paraphrase = ev.get("paraphrase") or ev.get("note")
        verified = ev.get("verification_status") == "verified"
        if snippet:
            title = "原文依据" if verified else "材料片段"
            text = str(snippet)
        elif paraphrase:
            title = "依据定位 / 核验提示"
            text = str(paraphrase)
        else:
            title = "依据定位"
            text = "当前结果提供了证据位置，但没有可直接展示的原文片段。"
        meta = {
            "证据ID": ref_id,
            "位置": _locator(ev),
        }
        ev_type = ev.get("evidence_type")
        if ev_type:
            meta["类型"] = ev_type
        blocks.append({
            "type": "callout",
            "role": "evidence" if snippet else "note",
            "title": title,
            "text": text,
            "meta": meta,
        })
    return blocks


def _add_statement(blocks: List[Dict[str, Any]], stmt: Any, ev_map: Dict[str, Dict[str, Any]], role: str = "body", label: str | None = None):
    text = _statement_text(stmt)
    if not text:
        return
    status = _statement_status(stmt)
    prefix = f"{label}：" if label else ""
    if status:
        prefix += f"[{status}] "
    blocks.append({"type": "paragraph", "role": role, "text": prefix + text})
    blocks.extend(_evidence_callouts(_statement_refs(stmt), ev_map))


def _heading(blocks: List[Dict[str, Any]], text: str, level: int = 1):
    blocks.append({"type": "heading", "role": f"heading{min(level,3)}", "level": level, "text": text})


def _as_list(items: Any) -> List[Any]:
    return items if isinstance(items, list) else []


def _research_value_rows(value: Any) -> List[List[str]]:
    rows = []
    if not isinstance(value, dict):
        return rows
    labels = {"methodological": "方法学价值", "empirical": "实证价值", "application": "应用价值"}
    for key, label in labels.items():
        v = value.get(key)
        if isinstance(v, dict):
            level = v.get("level") or v.get("rating") or ""
            rationale = v.get("rationale") or v.get("reason") or ""
            rows.append([label, str(level), str(rationale)])
        elif v is not None:
            rows.append([label, str(v), ""])
    return rows


def _paper_identity_meta(paper: Dict[str, Any]) -> Dict[str, Any]:
    identity = paper.get("identity") or {}
    meta = {}
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
    if paper.get("evidence_grade"):
        meta["Evidence Grade"] = paper.get("evidence_grade")
    sb = paper.get("source_boundary") or {}
    if sb.get("coverage"):
        meta["材料覆盖"] = sb.get("coverage")
    if sb.get("locator_mode"):
        meta["证据定位"] = sb.get("locator_mode")
    if sb.get("context_mode"):
        meta["外部核验"] = sb.get("context_mode")
    return meta


def _adapt_one_paper(paper: Dict[str, Any], index: int = 0, multi: bool = False) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    ev_map = {str(ev.get("id")): ev for ev in _as_list(paper.get("evidence_refs")) if isinstance(ev, dict) and ev.get("id")}

    identity = paper.get("identity") or {}
    paper_title = identity.get("title") or f"论文 {index+1}"
    if multi:
        if index:
            blocks.append({"type": "page_break", "role": "body"})
        _heading(blocks, paper_title, 1)

    # 01 Overview
    _heading(blocks, "01 论文速览", 1 if not multi else 2)
    jc = paper.get("judgment_card") or {}
    takeaway = jc.get("one_sentence_takeaway")
    if takeaway:
        blocks.append({"type": "paragraph", "role": "lead", "text": str(takeaway)})

    overview_rows = []
    if jc.get("evidence_strength"):
        overview_rows.append(["整体证据支持", jc.get("evidence_strength")])
    rp = jc.get("reading_priority")
    if isinstance(rp, dict):
        overview_rows.append(["阅读优先级", rp.get("level", "")])
        if rp.get("reason"):
            overview_rows.append(["阅读建议", rp.get("reason")])
    elif rp:
        overview_rows.append(["阅读优先级", rp])
    if jc.get("who_should_read"):
        overview_rows.append(["适合读者", "；".join(jc.get("who_should_read") or [])])
    if overview_rows:
        blocks.append({"type": "table", "role": "table", "headers": ["项目", "判断"], "rows": overview_rows})

    rv_rows = _research_value_rows(jc.get("research_value"))
    if rv_rows:
        blocks.append({"type": "table", "role": "table", "caption": "研究价值", "headers": ["维度", "等级", "理由"], "rows": rv_rows})

    # 02 Problem & Gap
    _heading(blocks, "02 研究问题与 Gap", 1 if not multi else 2)
    if paper.get("research_problem"):
        rp_obj = paper.get("research_problem") or {}
        if isinstance(rp_obj, dict):
            _add_statement(blocks, rp_obj.get("author_framing"), ev_map, label="作者表述")
            _add_statement(blocks, rp_obj.get("actual_problem"), ev_map, role="analysis", label="实际问题")
            _add_statement(blocks, rp_obj.get("claimed_gap"), ev_map, label="论文声称的 Gap")
            _add_statement(blocks, rp_obj.get("gap_assessment"), ev_map, role="analysis", label="Gap 判断")
    else:
        _add_statement(blocks, paper.get("research_question"), ev_map, label="研究问题")

    # 03 Method & Novelty
    _heading(blocks, "03 核心方法与真实创新", 1 if not multi else 2)
    method = paper.get("method_summary") or {}
    for key, label in [
        ("summary", "方法概述"),
        ("previous_approach", "Previous"),
        ("proposed_change", "Proposed"),
        ("mechanism", "Mechanism"),
        ("expected_benefit", "Expected Effect"),
    ]:
        _add_statement(blocks, method.get(key), ev_map, label=label)

    modules = method.get("main_modules") or method.get("modules") or []
    if modules:
        _heading(blocks, "核心模块", 2 if not multi else 3)
        for i, module in enumerate(modules, 1):
            if isinstance(module, dict) and "module_name" in module:
                _heading(blocks, f"{i}. {module.get('module_name')}", 3)
                rows = []
                for k, label in [
                    ("purpose", "作用"), ("input", "输入"), ("operation", "操作"),
                    ("output", "输出"), ("why_needed", "为什么需要"), ("measured_effect", "实验证据")
                ]:
                    if module.get(k):
                        rows.append([label, _text(module.get(k))])
                if rows:
                    blocks.append({"type": "table", "role": "table", "headers": ["项目", "内容"], "rows": rows})
                blocks.extend(_evidence_callouts([str(x) for x in module.get("evidence_refs", [])], ev_map))
            else:
                _add_statement(blocks, module, ev_map, label=f"模块 {i}")

    assumptions = method.get("assumptions") or []
    if assumptions:
        _heading(blocks, "关键假设", 2 if not multi else 3)
        for i, a in enumerate(assumptions, 1):
            if not isinstance(a, dict):
                blocks.append({"type": "paragraph", "role": "body", "text": f"A{i} {a}"})
                continue
            aid = a.get("assumption_id") or f"A{i}"
            atext = a.get("assumption_text") or a.get("text") or ""
            prov = a.get("provenance") or a.get("assumption_type") or ""
            risk = a.get("risk_level") or ("high" if a.get("assumption_type") == "high_risk" else "")
            body = f"{aid} {atext}"
            meta = []
            if prov:
                meta.append(f"来源性质：{prov}")
            if risk:
                meta.append(f"风险：{risk}")
            if a.get("risk_note") or a.get("failure_mode"):
                meta.append(f"失效后果：{a.get('failure_mode') or a.get('risk_note')}")
            if meta:
                body += "\n" + "；".join(meta)
            blocks.append({"type": "callout", "role": "analysis" if risk != "high" else "warning", "title": "关键假设", "text": body})
            blocks.extend(_evidence_callouts([str(x) for x in a.get("evidence_refs", [])], ev_map))

    novelty = paper.get("novelty")
    if isinstance(novelty, dict):
        _heading(blocks, "创新判断", 2 if not multi else 3)
        if novelty.get("paper_relative_delta"):
            blocks.append({"type": "paragraph", "role": "analysis", "text": "相对本文 prior work 的变化：" + _text(novelty.get("paper_relative_delta"))})
        if novelty.get("field_novelty"):
            blocks.append({"type": "paragraph", "role": "analysis", "text": "领域创新核验：" + _text(novelty.get("field_novelty"))})
        if novelty.get("verification_status"):
            blocks.append({"type": "callout", "role": "note", "title": "Novelty Verification", "text": str(novelty.get("verification_status"))})
        blocks.extend(_evidence_callouts([str(x) for x in novelty.get("evidence_refs", [])], ev_map))
    else:
        contributions = paper.get("contributions") or []
        if contributions:
            _heading(blocks, "贡献 / 创新", 2 if not multi else 3)
            for i, c in enumerate(contributions, 1):
                _add_statement(blocks, c, ev_map, label=f"贡献 {i}")

    # 04 Experiments & evidence
    _heading(blocks, "04 实验与证据", 1 if not multi else 2)
    findings = paper.get("evaluation_or_findings") or []
    if findings:
        _heading(blocks, "主要结果", 2 if not multi else 3)
        for i, f in enumerate(findings, 1):
            _add_statement(blocks, f, ev_map, label=f"结果 {i}")

    claims = paper.get("claim_evidence") or []
    if claims:
        _heading(blocks, "Claim–Evidence", 2 if not multi else 3)
        for i, item in enumerate(claims, 1):
            if not isinstance(item, dict):
                continue
            claim = item.get("claim_text") or item.get("claim") or ""
            if isinstance(claim, dict):
                claim_text = _statement_text(claim)
                refs = _statement_refs(claim)
            else:
                claim_text = _text(claim)
                refs = []
            refs = [str(x) for x in (item.get("evidence_refs") or refs)]
            rows = [
                ["Claim", claim_text],
                ["支持程度", item.get("support_strength", "")],
                ["为什么", item.get("support_reason", "")],
                ["适用边界", item.get("scope_boundary", "")],
                ["不能进一步证明", item.get("unsupported_stronger_claim", "")],
                ["还需要什么", item.get("what_would_strengthen_it", "")],
            ]
            rows = [[k, v] for k, v in rows if v not in (None, "")]
            blocks.append({"type": "table", "role": "table", "caption": f"Claim {i}", "headers": ["项目", "内容"], "rows": rows})
            blocks.extend(_evidence_callouts(refs, ev_map))

    audit = paper.get("evidence_audit") or {}
    if audit:
        if audit.get("overall_support"):
            blocks.append({"type": "callout", "role": "analysis", "title": "整体证据支持", "text": str(audit.get("overall_support"))})
        for key, label, role in [
            ("strongly_supported", "充分支持", "analysis"),
            ("weakly_supported", "部分/较弱支持", "warning"),
            ("unsupported_or_overclaimed", "证据不足或过度外推", "limitation"),
        ]:
            vals = audit.get(key) or []
            if vals:
                _heading(blocks, label, 3)
                for v in vals:
                    _add_statement(blocks, v, ev_map, role=role)
        missing = audit.get("missing_evidence") or []
        if missing:
            blocks.append({"type": "list", "role": "warning", "ordered": False, "items": [str(x) for x in missing]})

    # 05 Critical review
    _heading(blocks, "05 批判性评价", 1 if not multi else 2)
    author_limits = paper.get("author_acknowledged_limitations")
    if author_limits:
        _heading(blocks, "作者明确承认的局限", 2 if not multi else 3)
        for item in author_limits:
            _add_statement(blocks, item, ev_map, role="limitation")

    limits = paper.get("limitations_or_unknowns") or []
    if limits:
        _heading(blocks, "局限与未知", 2 if not multi else 3)
        for item in limits:
            _add_statement(blocks, item, ev_map, role="limitation")

    crit = paper.get("critical_review") or {}
    main_limits = crit.get("analysis_limitations") or crit.get("main_limitations") or []
    if main_limits:
        _heading(blocks, "PaperScope 分析出的局限", 2 if not multi else 3)
        for item in main_limits:
            _add_statement(blocks, item, ev_map, role="limitation")

    fragile = crit.get("fragile_assumptions") or []
    if fragile:
        _heading(blocks, "脆弱假设", 2 if not multi else 3)
        for i, item in enumerate(fragile, 1):
            if isinstance(item, dict):
                aid = item.get("assumption_id") or f"A{i}"
                text = item.get("assumption_text") or ""
                failure = item.get("failure_mode") or ""
                blocks.append({"type": "callout", "role": "warning", "title": f"脆弱假设 {aid}", "text": f"{text}\nFailure mode：{failure}".strip()})
                blocks.extend(_evidence_callouts([str(x) for x in item.get("evidence_refs", [])], ev_map))

    questions = crit.get("reviewer_questions") or []
    if questions:
        _heading(blocks, "Reviewer Questions", 2 if not multi else 3)
        blocks.append({"type": "list", "role": "warning", "ordered": True, "items": [str(x) for x in questions[:5]]})

    contradictions = paper.get("contradictions") or []
    if contradictions:
        _heading(blocks, "材料中的不一致", 2 if not multi else 3)
        for item in contradictions:
            if not isinstance(item, dict):
                continue
            text = item.get("description") or "发现材料不一致"
            meta = {}
            if item.get("impact"):
                meta["影响"] = item.get("impact")
            if item.get("resolution_needed"):
                meta["如何解决"] = item.get("resolution_needed")
            blocks.append({"type": "callout", "role": "warning", "title": "材料不一致", "text": text, "meta": meta})
            blocks.extend(_evidence_callouts([x for x in [item.get("source_a"), item.get("source_b")] if x], ev_map))

    # 06 Open questions
    _heading(blocks, "06 开放问题与精读建议", 1 if not multi else 2)
    oqs = paper.get("open_questions") or []
    if oqs:
        for i, q in enumerate(oqs, 1):
            if isinstance(q, dict):
                q_text = q.get("question") or ""
                origin = q.get("origin") or q.get("status") or ""
                why = q.get("why_it_matters") or ""
                nxt = q.get("suggested_validation") or q.get("suggested_next_step") or ""
                body = f"问题：{q_text}"
                if origin:
                    body += f"\n来源：{origin}"
                if why:
                    body += f"\n为什么重要：{why}"
                if nxt:
                    body += f"\n建议如何验证：{nxt}"
                blocks.append({"type": "callout", "role": "analysis", "title": f"Open Question {i}", "text": body})
                blocks.extend(_evidence_callouts([str(x) for x in q.get("evidence_refs", [])], ev_map))
            else:
                blocks.append({"type": "paragraph", "role": "analysis", "text": str(q)})
    else:
        blocks.append({"type": "paragraph", "role": "note", "text": "当前结果未提供开放问题。"})

    return blocks


def adapt(data: Dict[str, Any]) -> Dict[str, Any]:
    papers = data.get("papers") or []
    if not papers:
        raise ValueError("Deep-reading result contains no papers.")

    first = papers[0]
    first_identity = first.get("identity") or {}
    base_title = first_identity.get("title") or "AI论文精读报告"
    multi = len(papers) > 1
    title = "AI论文精读报告" if multi else f"{base_title} — AI论文精读报告"

    metadata = _paper_identity_meta(first)
    if multi:
        metadata["论文数量"] = len(papers)
    if data.get("analysis_type"):
        metadata["分析类型"] = data.get("analysis_type")
    if data.get("schema_version"):
        metadata["精读Schema"] = data.get("schema_version")

    blocks: List[Dict[str, Any]] = []
    for i, paper in enumerate(papers):
        blocks.extend(_adapt_one_paper(paper, i, multi))

    global_limits = data.get("global_limitations") or []
    if global_limits:
        _heading(blocks, "全局材料限制", 1)
        blocks.append({"type": "list", "role": "warning", "ordered": False, "items": [str(x) for x in global_limits]})

    return {
        "schema_version": "1.0",
        "document_id": f"deep-reading-{first.get('paper_id', 'report')}",
        "document_kind": "ai_deep_reading",
        "language": "zh-CN",
        "title": title,
        "subtitle": "Evidence-aware academic paper deep reading report",
        "metadata": metadata,
        "blocks": blocks,
    }

from __future__ import annotations

from typing import Any, Dict

from adapters.deep_reading_to_document import adapt as adapt_deep_reading


def _analysis_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(data.get("analysis"), dict):
        return data["analysis"]

    nested = data.get("data")
    if isinstance(nested, dict):
        if isinstance(nested.get("analysis"), dict):
            return nested["analysis"]
        result = nested.get("result")
        if isinstance(result, dict) and isinstance(result.get("analysis"), dict):
            return result["analysis"]

    if isinstance(data.get("papers"), list):
        return data

    raise ValueError("AI Reader payload does not contain a deep-reading analysis object.")


def adapt(data: Dict[str, Any]) -> Dict[str, Any]:
    return adapt_deep_reading(_analysis_payload(data))

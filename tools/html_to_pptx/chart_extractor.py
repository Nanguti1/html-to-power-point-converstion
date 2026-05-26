from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup

from .utils import parse_chart_type, parse_index_axis, parse_js_array_literal


@dataclass
class ChartInfo:
    chart_type: str
    index_axis: Optional[str]
    labels: List[str]
    values: List[float]
    counts: List[float]
    background_color: str


def _parse_required_array(script_text: str, name: str):
    raw = parse_js_array_literal(script_text, name)
    if not raw:
        raise ValueError(f"Missing '{name}' array in Chart.js script")
    try:
        return ast.literal_eval(raw)
    except Exception as exc:
        raise ValueError(f"Unable to parse '{name}' array in Chart.js script") from exc


def _find_chart_script(scripts: List[str]) -> Optional[str]:
    for script in scripts:
        if "new Chart(" in script:
            return script
    return None


def extract_chart_info(html_text: str) -> ChartInfo:
    soup = BeautifulSoup(html_text, "lxml")

    # Ignore external scripts (src=...) and parse only inline JS authored in slide HTML.
    inline_scripts = [
        s.get_text("\n", strip=False)
        for s in soup.find_all("script")
        if not s.get("src") and s.get_text(strip=True)
    ]

    chart_script = _find_chart_script(inline_scripts)
    if not chart_script:
        raise ValueError("Could not locate inline Chart.js script block containing 'new Chart('")

    # Some exports split array declarations and chart construction across inline scripts.
    combined_inline_js = "\n\n".join(inline_scripts)

    labels = list(_parse_required_array(combined_inline_js, "labels"))
    values = [float(x) for x in _parse_required_array(combined_inline_js, "values")]

    counts_raw = parse_js_array_literal(combined_inline_js, "counts")
    if counts_raw:
        counts = [float(x) for x in ast.literal_eval(counts_raw)]
    else:
        counts = [0.0 for _ in values]

    cm = re.search(r"backgroundColor\s*:\s*['\"]([^'\"]+)['\"]", chart_script)
    color = cm.group(1) if cm else "#A2C037"

    if len(counts) != len(values):
        counts = (counts + [0.0] * len(values))[: len(values)]

    return ChartInfo(parse_chart_type(chart_script), parse_index_axis(chart_script), labels, values, counts, color)

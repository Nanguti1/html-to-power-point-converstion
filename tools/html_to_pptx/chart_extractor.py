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
    # Prefer the script that constructs a chart and has data arrays.
    for script in scripts:
        if "new Chart(" not in script:
            continue
        if parse_js_array_literal(script, "labels") and parse_js_array_literal(script, "values"):
            return script
    # Fallback: any chart-construction script.
    for script in scripts:
        if "new Chart(" in script:
            return script
    return None


def extract_chart_info(html_text: str) -> ChartInfo:
    soup = BeautifulSoup(html_text, "lxml")
    scripts = [s.get_text("\n", strip=False) for s in soup.find_all("script") if s.get_text(strip=True)]

    chart_script = _find_chart_script(scripts)
    if not chart_script:
        raise ValueError("Could not locate Chart.js script block containing 'new Chart('")

    labels = list(_parse_required_array(chart_script, "labels"))
    values = [float(x) for x in _parse_required_array(chart_script, "values")]

    # counts is required per template, but fallback to 0s if absent for resilience.
    counts_raw = parse_js_array_literal(chart_script, "counts")
    if counts_raw:
        counts = [float(x) for x in ast.literal_eval(counts_raw)]
    else:
        counts = [0.0 for _ in values]

    cm = re.search(r"backgroundColor\s*:\s*['\"]([^'\"]+)['\"]", chart_script)
    color = cm.group(1) if cm else "#A2C037"

    if len(counts) != len(values):
        counts = (counts + [0.0] * len(values))[: len(values)]

    return ChartInfo(parse_chart_type(chart_script), parse_index_axis(chart_script), labels, values, counts, color)

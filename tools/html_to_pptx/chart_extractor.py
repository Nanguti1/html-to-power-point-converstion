from __future__ import annotations
import ast, re
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

def extract_chart_info(html_text: str) -> ChartInfo:
    soup = BeautifulSoup(html_text, 'lxml')
    scripts = [s.get_text('\n', strip=False) for s in soup.find_all('script') if s.get_text(strip=True)]
    chart_script = next((s for s in scripts if 'new Chart(' in s and 'const labels' in s and 'const values' in s), None)
    if not chart_script:
        raise ValueError('Could not locate Chart.js script block')
    labels = ast.literal_eval(parse_js_array_literal(chart_script,'labels'))
    values = [float(x) for x in ast.literal_eval(parse_js_array_literal(chart_script,'values'))]
    counts = [float(x) for x in ast.literal_eval(parse_js_array_literal(chart_script,'counts'))]
    cm = re.search(r"backgroundColor\s*:\s*['\"]([^'\"]+)['\"]", chart_script)
    color = cm.group(1) if cm else '#A2C037'
    return ChartInfo(parse_chart_type(chart_script), parse_index_axis(chart_script), list(labels), values, counts, color)
